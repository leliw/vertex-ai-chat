import { Component, ElementRef, OnDestroy, OnInit, ViewChild, ViewEncapsulation, inject } from '@angular/core';
import { ChatService, ChatSessionHeader, ChatSession } from '../chat.service';
import { AsyncPipe, CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatSidenavContainer, MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MarkdownPipe } from '../shared/markdown.pipe';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatToolbarModule } from '@angular/material/toolbar';
import { Observable, map, shareReplay } from 'rxjs';
import { AuthService } from '../shared/auth/auth.service';
import { ConfigService } from '../shared/config/config.service';


@Component({
    selector: 'app-chat',
    standalone: true,
    imports: [CommonModule,
        MatToolbarModule,
        MatButtonModule,
        MatSidenavModule,
        MatListModule,
        MatIconModule,
        AsyncPipe,
        FormsModule, MatInputModule, MatTooltipModule, MarkdownPipe],
    templateUrl: './chat.component.html',
    styleUrl: './chat.component.css',
    encapsulation: ViewEncapsulation.None,
})
export class ChatComponent implements OnInit, OnDestroy {

    @ViewChild(MatSidenavContainer) drawerContainer!: MatSidenavContainer;
    @ViewChild('container') container!: ElementRef;

    history: ChatSessionHeader[] = [];
    session!: ChatSession;
    newMessage = '';
    waitingForResponse = false;
    connected = false;
    currentAnswer = '';
    currentTypeIndex = 0;

    private breakpointObserver = inject(BreakpointObserver);

    isHandset$: Observable<boolean> = this.breakpointObserver.observe(Breakpoints.Handset)
        .pipe(
            map(result => result.matches),
            shareReplay()
        );
    isHandset!: boolean;

    constructor(private chatService: ChatService, public authService: AuthService, private config: ConfigService) {
        // Get the initial messages from the server
        this.newChat()
        this.chatService.get_all().subscribe(history => {
            this.history = history;
            setTimeout(() => this.drawerContainer.updateContentMargins(), 100);
        });
        this.isHandset$.subscribe(isHandset => this.isHandset = isHandset);
    }

    ngOnInit(): void {
        this.chatService.connect();
        this.chatService.connected().subscribe(connected => this.connected = connected);
    }

    ngOnDestroy(): void {
        this.chatService.disconect();
    }

    sendMessageAsync() {
        // Send message to the server and process the response asynchronously
        if (this.newMessage.trim().length > 0) {
            if (this.session.history.length == 0)
                this.history.unshift({
                    chat_session_id: this.session.chat_session_id,
                    user: "",
                    created: new Date(),
                    summary: this.newMessage
                });
            const message = { author: "user", content: this.newMessage }
            this.session.history.push(message);
            this.scrollBottom();
            this.newMessage = '';
            this.waitingForResponse = true;
            this.currentAnswer = '';
            this.currentTypeIndex = 0;
            this.session.history.push({ author: "ai", content: "" });
            this.chatService.send_async(message).subscribe({
                next: (chunk) => {
                    this.currentAnswer += chunk;
                    if (this.currentTypeIndex == 0)
                        this.typeAnswer();
                },
                complete: () => {
                    this.waitingForResponse = false;
                }
            });
        }
    }
    typeAnswer() {
        // Simulate typing effect
        if (this.currentTypeIndex < this.currentAnswer.length) {
            this.session.history[this.session.history.length - 1].content += this.currentAnswer[this.currentTypeIndex];
            this.currentTypeIndex++;
            this.scrollBottom();
            setTimeout(() => this.typeAnswer(), 15);
        } else if (this.waitingForResponse)
            setTimeout(() => this.typeAnswer(), 15);
    }

    scrollBottom(): void {
        // Scroll to the bottom of the chat container
        setTimeout(() => this.container.nativeElement.scrollTop = this.container.nativeElement.scrollHeight, 100);
    }

    newChat() {
        this.chatService.new().subscribe(session => {
            this.session = session;
            if (this.isHandset)
                this.drawerContainer.close();
        });
    }

    loadChat(chat_session_id: string) {
        this.chatService.get(chat_session_id).subscribe(session => {
            this.session = session;
            if (this.isHandset)
                this.drawerContainer.close();
            setTimeout(() => this.scrollBottom(), 100);
        });

    }

    deleteChat(chat_session_id: string) {
        this.chatService.delete(chat_session_id).subscribe(
            () => {
                if (this.session.chat_session_id == chat_session_id)
                    this.newChat();
                this.chatService.get_all().subscribe(history => this.history = history);
            }
        );
    }

}