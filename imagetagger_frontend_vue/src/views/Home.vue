<template>
    <div class="home">
        HOME!

        <apos-button/>
	    
	    <router-link to="/bla">Bla</router-link>
    </div>
</template>

<script>
	import Button from 'components/Button'
	
    export default {
        name: 'Home',
	    
	    components: {
        	'AposButton': Button
	    },
        
        data() {
            return {
            
            }
        },
        
        computed: {
        
        },
        
        methods: {
        
        }
    }
</script>

<style lang="scss">
    .home {
    
    }
</style>
