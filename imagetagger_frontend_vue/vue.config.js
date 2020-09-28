// eslint-disable-next-line @typescript-eslint/no-var-requires
const path = require("path")

module.exports = {
    lintOnSave: false,

    css: {
        loaderOptions: {
            sass: {
                sassOptions: {
                    includePaths: [path.resolve(__dirname, "node_modules"), path.resolve(__dirname)]
                }
            }
        }
    },

    transpileDependencies: [
        "vuetify"
    ]
}
