<template>
  <div class="alert" role="alert" v-bind:id="id" v-bind:class="'alert-' + variant">
    {{ msg }}
  </div>
</template>

<script>
export default {
  name: 'Alert',  //this is the name of the component
  props: ['id', 'variant', 'msg']
}
</script>