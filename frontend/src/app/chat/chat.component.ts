import { AfterViewChecked, Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { ChatService, Message } from '../chat.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';


@Component({
    selector: 'app-chat',
    standalone: true,
    imports: [CommonModule, FormsModule, MatIconModule, MatTooltipModule],
    templateUrl: './chat.component.html',
    styleUrl: './chat.component.css'
})
export class ChatComponent implements OnInit, OnDestroy, AfterViewChecked {

    @ViewChild('container') container!: ElementRef;

    messages: Message[] = []
    newMessage = '';
    waitingForResponse = false;
    connected = false;

    constructor(private chatService: ChatService) { }

    ngOnInit(): void {
        this.chatService.connect();
        this.chatService.connected().subscribe(connected => this.connected = connected);
    }

    ngOnDestroy(): void {
        this.chatService.disconect();
    }

    sendMessage() {
        this.messages.push({ author: "user", "content": this.newMessage });
        if (this.newMessage.trim().length > 0) {
            this.chatService.send(this.newMessage);
            this.waitingForResponse = true;
            this.newMessage = '';
        }
    }

    ngAfterViewChecked(): void {
        this.container.nativeElement.scrollTop = this.container.nativeElement.scrollHeight;
    }
}