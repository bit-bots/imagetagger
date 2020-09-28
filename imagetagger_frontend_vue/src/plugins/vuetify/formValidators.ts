type Rule = (value: unknown) => boolean | string

export const required: Rule = function (value) {
    if (value != null && value != "" && value != [])
        return true
    else
        return "Field is required"
}
