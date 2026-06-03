import time
import traceback
import json
import os
from datetime import datetime
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# 日志目录
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 日志文件路径
ACTION_LOG_FILE = os.path.join(LOG_DIR, "actions.log")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "errors.log")


def write_log(file_path: str, log_data: dict):
    """写入JSON格式的日志到文件"""
    try:
        log_data["timestamp"] = datetime.now().isoformat()
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"写日志失败: {e}")


class LogMiddleware(BaseHTTPMiddleware):
    """日志中间件 - 记录用户操作和程序错误"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # 获取基本信息
        method = request.method
        url = str(request.url)
        ip = request.client.host if request.client else None

        # 获取用户ID（从token解析）
        user_id = None
        token = request.headers.get("Authorization")
        if token and token.startswith("Bearer "):
            token = token[7:]
            try:
                import jwt
                from core.config import settings
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                user_id = payload.get("sub")
            except Exception:
                pass

        # 从 URL 提取目标信息
        path_parts = url.split("/")
        target_type = None
        target_id = None
        
        for i, part in enumerate(path_parts):
            if part in ["users", "user"]:
                target_type = "User"
                if i + 1 < len(path_parts) and path_parts[i + 1].isdigit():
                    target_id = path_parts[i + 1]
                break
            elif part in ["articles", "article"]:
                target_type = "Article"
                if i + 1 < len(path_parts) and path_parts[i + 1].isdigit():
                    target_id = path_parts[i + 1]
                break
        
        # 记录增删改操作（所有 POST/PUT/DELETE 请求）
        if method in ["POST", "PUT", "DELETE"]:
            action_map = {"POST": "CREATE", "PUT": "UPDATE", "DELETE": "DELETE"}
            
            write_log(ACTION_LOG_FILE, {
                "user_id": user_id,
                "action": action_map.get(method),
                "target_type": target_type or "Other",
                "target_id": target_id,
                "method": method,
                "url": url,
                "ip": ip,
                "success": True
            })

        # 执行请求并捕获错误
        response = None
        try:
            response = await call_next(request)
        except Exception as e:
            # 记录错误日志（仅记录真正的异常，不包括HTTPException）
            write_log(ERROR_LOG_FILE, {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc(),
                "user_id": user_id,
                "url": url,
                "method": method,
                "ip": ip
            })
            # 重新抛出异常让FastAPI处理
            raise
        
        # 记录响应状态码，如果状态码 >= 400，也记录到错误日志
        if response and response.status_code >= 400:
            write_log(ERROR_LOG_FILE, {
                "error_type": "HTTP_ERROR",
                "status_code": response.status_code,
                "error_message": f"HTTP {response.status_code}",
                "user_id": user_id,
                "url": url,
                "method": method,
                "ip": ip
            })
        
        return response