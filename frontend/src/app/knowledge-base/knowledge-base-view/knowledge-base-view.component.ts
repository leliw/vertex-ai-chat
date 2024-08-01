import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { KnowledgeBaseService } from '../knowledge-base.service';
import { MarkdownPipe } from "../../shared/markdown.pipe";
import { MatChipsModule } from '@angular/material/chips';

@Component({
    selector: 'app-knowledge-base-view',
    standalone: true,
    imports: [
        MatChipsModule,
        MarkdownPipe
    ],
    templateUrl: './knowledge-base-view.component.html',
    styleUrl: './knowledge-base-view.component.css'
})
export class KnowledgeBaseViewComponent {

    public title!: string;
    public content!: string;
    public keywords: string[] = [];

    constructor(activatedRoute: ActivatedRoute, knowledgeBaseService: KnowledgeBaseService) {
        const item_id = activatedRoute.snapshot.params['id'];
        knowledgeBaseService.getItem(item_id).subscribe(item => {
            this.title = item.title;
            this.content = item.content;
            this.keywords = item.keywords || [];
        });
    }
}
