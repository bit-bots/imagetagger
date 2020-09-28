module.exports = {
    root: true,
    env: {
        node: true
    },
    plugins: ["@typescript-eslint"],
    extends: ["eslint:recommended", "plugin:@typescript-eslint/recommended", "plugin:vue/essential",],
    parserOptions: {
        parser: "@typescript-eslint/parser"
    },
    rules: {
        "no-console": process.env.NODE_ENV === "production" ? "error" : "warn",
        "no-debugger": process.env.NODE_ENV === "production" ? "error" : "warn",
    },
}
