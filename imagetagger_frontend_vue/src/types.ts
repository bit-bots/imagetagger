import {RawLocation} from "vue-router"

export class CardTabDefinition {
    public name: string
    public link: RawLocation

    constructor(name: string, link: RawLocation) {
        this.name = name
        this.link = link
    }
}
