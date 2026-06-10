<template>
  <PostPageNew v-if="useNavV2" />
  <PostPageOld v-else />
</template>

<script setup>
import { useNavV2 } from '@/composables/useStyleSwitch'
import PostPageNew from './PostPage.vue'
import PostPageOld from './PostPageOld.vue'
</script>
