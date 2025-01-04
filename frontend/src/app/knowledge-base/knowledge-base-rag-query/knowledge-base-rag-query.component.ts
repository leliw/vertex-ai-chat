
import { Component } from '@angular/core';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { MatChipsModule } from '@angular/material/chips';
import { MarkdownPipe } from "../../shared/markdown.pipe";
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';


interface RagResult {
    item_id: string;
    title: string;
    keywords: string[];
    content: string;
    metadata: { [key: string]: string };
}

@Component({
    selector: 'app-knowledge-base-rag-query',
    standalone: true,
    imports: [
        CommonModule,
        ReactiveFormsModule,
        MatExpansionModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatChipsModule,
        MatProgressBarModule,
        MarkdownPipe,
        MatIconModule,
    ],
    templateUrl: './knowledge-base-rag-query.component.html',
    styleUrl: './knowledge-base-rag-query.component.css'
})
export class KnowledgeBaseRagQueryComponent {
    query: string = "";
    searchForm: FormGroup;
    results: RagResult[] = [];
    isLoading: boolean = false;
    apiUrl: string = '/api/knowledge-base/find-nearest';

    constructor(private http: HttpClient, private fb: FormBuilder) {
        this.searchForm = this.fb.group({
            query: ['', Validators.required],
        });
    }

    onSubmit(): void {
        if (this.searchForm.valid) {
            this.isLoading = true;
            this.results = [];
            const query = this.searchForm.get('query')?.value;
            this.http.post<RagResult[]>(this.apiUrl, { text: query }).subscribe({
                next: (data) => {
                    this.results = data;
                    this.isLoading = false;
                },
                error: (error) => {
                    console.error('Błąd podczas wyszukiwania:', error);
                    this.isLoading = false;
                },
            });
        }
    }

    isEmpty(item: { [key: string]: string }): boolean {
        return Object.keys(item).length === 0;
    }

}
