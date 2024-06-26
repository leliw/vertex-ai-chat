import { Component, OnDestroy, OnInit, ViewChild, ViewEncapsulation, inject } from '@angular/core';
import { ChatService } from '../chat.service';
import { AsyncPipe, CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatSidenavContainer, MatSidenavModule } from '@angular/material/sidenav';
import { MatChipsModule } from '@angular/material/chips';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatMenuModule } from '@angular/material/menu';
import { MarkdownPipe } from '../../shared/markdown.pipe';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatToolbarModule } from '@angular/material/toolbar';
import { Observable, Subscription, filter, firstValueFrom, map, shareReplay } from 'rxjs';
import { AuthService } from '../../shared/auth/auth.service';
import { ConfigService } from '../../shared/config/config.service';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ChatListComponent } from "../chat-list/chat-list.component";
import { ChatViewComponent } from "../chat-view/chat-view.component";
import { SessionService } from '../../shared/session.service';
import { SpeechRecognitionButtonComponent } from "../../shared/speech-recognition-button/speech-recognition-button.component";


@Component({
    selector: 'app-chat',
    standalone: true,
    templateUrl: './chat-page.component.html',
    styleUrl: './chat-page.component.css',
    encapsulation: ViewEncapsulation.None,
    imports: [CommonModule,
        MatToolbarModule,
        MatChipsModule,
        MatButtonModule,
        MatSidenavModule,
        MatListModule,
        MatIconModule,
        AsyncPipe,
        FormsModule, MatInputModule, MatTooltipModule, MatMenuModule, MarkdownPipe, MatProgressSpinnerModule, ChatListComponent, ChatViewComponent, SpeechRecognitionButtonComponent]
})
export class ChatPageComponent implements OnInit, OnDestroy {

    @ViewChild(MatSidenavContainer) drawerContainer!: MatSidenavContainer;
    @ViewChild('container') chatView!: ChatViewComponent;

    models: string[] = [];
    model!: string;

    sessionChanged = false;
    newMessage = '';
    progressSpinner = false;


    private dataSubscription!: Subscription;
    private breakpointObserver = inject(BreakpointObserver);

    isHandset$: Observable<boolean> = this.breakpointObserver.observe(Breakpoints.Handset)
        .pipe(
            map(result => result.matches),
            shareReplay()
        );
    isHandset!: boolean;

    constructor(public authService: AuthService, private config: ConfigService, public chatService: ChatService, public sessionService: SessionService) {
        // Get the initial messages from the server
        this.chatService.get_models().subscribe(models => {
            this.models = models;
            this.model = models[0];
            this.chatService.get_all().subscribe(chats => {
                this.newChat()
                setTimeout(() => this.drawerContainer.updateContentMargins(), 100);
            });
        });
        this.isHandset$.subscribe(isHandset => this.isHandset = isHandset);
    }

    ngOnInit(): void {
        this.chatService.connect();
    }

    ngOnDestroy(): void {
        this.chatService.disconect();
    }

    setModel(model: string) {
        this.model = model;
    }

    async sendMessageAsync() {
        // Send message to the server and process the response asynchronously
        if (this.newMessage.trim().length > 0) {
            const files = this.sessionService.selectedFiles.map(file => { return { name: file.name, mime_type: file.type } })
            const message = { author: "user", content: this.newMessage, files: files };

            if (this.sessionChanged) {
                await firstValueFrom(this.chatService.putChatSession(this.chatService.chat));
                this.sessionChanged = false;
            }
            if (this.sessionService.isUploading$.value)
                await firstValueFrom(this.sessionService.isUploading$.pipe(filter(ul => !ul)));
            this.sessionService.clearFiles()
            this.chatService.chat.history.push(message);
            const newMessage = { author: "user", content: this.newMessage }
            this.chatView.scrollBottom();
            this.newMessage = '';
            this.chatService.waitingForResponse = true;
            this.chatView.startTyping()
            this.chatService.chat.history.push({ author: "ai", content: "" });
            this.dataSubscription = this.chatService.send_async(this.model, newMessage).subscribe({
                next: (chunk) => {
                    if (chunk.type == "text") {
                        this.chatView.addAnswerChunk(chunk.value);
                    } else if (chunk.type.startsWith("error")) {
                        this.chatView.stopTyping()
                        if (this.chatService.chat.history[this.chatService.chat.history.length - 1].author == "ai")
                            this.chatService.chat.history.pop();
                        const errorClass = chunk.type.split(":")[1];
                        const errorMessage = "```\n" + chunk.value + "\n```"
                        this.chatService.chat.history.push({ author: "error", content: `### ${errorClass}\n\n${errorMessage}` });
                        setTimeout(() => this.chatView.scrollBottom(), 100);
                    }
                },
                complete: () => {
                    this.chatService.waitingForResponse = false;
                }
            });
        }
    }

    newChat() {
        this.loadChat('_NEW_');
    }

    loadChat(chat_session_id: string) {
        setTimeout(() => this.progressSpinner = this.chatService.isLoading, 500);
        this.chatService.get(chat_session_id).subscribe(() => {
            if (this.isHandset)
                this.drawerContainer.close();
            setTimeout(() => this.chatView.scrollBottom(), 100);
            this.progressSpinner = false;
            this.newMessage = '';
            this.sessionService.clearFiles()
            this.sessionChanged = false;
        });

    }

    cancelGenerating() {
        if (this.chatService.waitingForResponse) {
            // Cancel the current request
            this.dataSubscription.unsubscribe();
            if (this.chatService.chat.history[this.chatService.chat.history.length - 1].author == "ai")
                this.chatService.chat.history.pop();
            const question = this.chatService.chat.history.pop();
            if (question)
                this.newMessage = question.content ?? '';
            this.chatService.putChatSession(this.chatService.chat).subscribe();
        } else {
            // Stop typing
            this.chatView.stopTyping();
        }
    }

    deleteChat(chat_session_id: string) {
        if (this.chatService.chat.chat_session_id == chat_session_id)
            this.newChat();
    }

    changeMessage(index: number) {
        this.newMessage = this.chatService.chat.history[index].content?.trim() ?? '';
        this.sessionService.clearFiles()
        this.chatService.chat.history[index].files?.forEach(file => {
            this.sessionService.selectedFiles.push(new File([], file.name));
            this.sessionService.uploadProgress.push(100);
        });
        const newHistory = this.chatService.chat.history.slice(0, index);
        this.chatService.chat.history = newHistory;
        this.sessionChanged = true;
    }

    sendingMessageDisabled(): boolean {
        return this.chatService.isLoading || this.chatService.waitingForResponse || this.chatService.isTyping;
    }

}