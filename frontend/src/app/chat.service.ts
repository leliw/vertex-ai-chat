import { Injectable } from '@angular/core';

export interface Message {
    author: string;
    content?: string;
}

@Injectable({
    providedIn: 'root'
})
export class ChatService {

    constructor() { }
}
