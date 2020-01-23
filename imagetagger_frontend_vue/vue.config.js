var path = require("path")

module.exports = {
    lintOnSave: false,

    configureWebpack: config => {
        config.resolve.alias["@views"] = path.resolve(__dirname, "src", "views")
        config.resolve.alias["@components"] = path.resolve(
            __dirname,
            "src",
            "components"
        )
        config.resolve.alias["assets"] = path.resolve(__dirname, "src", "assets")
    }
}
