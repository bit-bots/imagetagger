<template>
    <div class="button">
        <button @click="text = 'hi'">{{ text }}</button>
    </div>
</template>

<script>
    export default {
        name: 'Button',
        
        data() {
            return {
                text: 'Button'
            }
        },
        
        computed: {
        
        },
        
        methods: {
        
        }
    }
</script>

<style lang="scss">
    .button {
     
	    button {
		    background: red;
		    color: #fff;
		    border: 1px solid green;
		    
		    padding: 8px 12px;
		    border-radius: 900px;
	    }
    }
</style>
