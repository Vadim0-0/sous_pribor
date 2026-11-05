<script setup lang="ts">

  interface Props {
    disabled?: boolean
    label?: string
    id?: string
    class?: string
  };

  const props = withDefaults(defineProps<Props>(), {
    type: 'button',
    disabled: false,
    label: '',
    id: undefined,
    class: '',
    styleType: 'default',
  });
</script>

<template>
  <button
    :class="['ui-btn', props.class]"
    :id="props.id"
    :disabled="props.disabled"
    v-bind="$attrs"
    
  >
  <slot />
</button>
</template>

<style lang="scss">
  @use './uiButton.scss';
</style>