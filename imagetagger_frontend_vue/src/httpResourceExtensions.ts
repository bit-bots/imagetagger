export class Url {
    private parts: string[]
    private getArgs: {key: string, value: string | number}[]
    private appendSlash: boolean

    constructor(base: string, appendSlash = true) {
        this.parts = base.split("/")
        this.getArgs = []
        this.appendSlash = appendSlash
    }

    public addPart(part: string | number): void {
        this.parts.push(part.toString())
    }

    public addGetArg(key: string, value: string | number): void {
        this.getArgs.push({key: key, value: value})
    }

    toString(): string {
        let base = this.parts.join("/")
        let args = ""

        if (this.appendSlash)
            base += "/"

        for (const iarg of this.getArgs) {
            if (args === "") {
                args = `?${iarg.key}=${iarg.value}`
            } else {
                args += `&${iarg.key}=${iarg.value}`
            }

        }

        return base + args
    }
}
