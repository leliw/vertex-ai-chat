import { Component, inject } from '@angular/core';

import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { KnowledgeBaseItem, KnowledgeBaseService } from '../knowledge-base.service';
import { ActivatedRoute, Router } from '@angular/router';
import { MatChipInputEvent, MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';


@Component({
    selector: 'app-knowledge-base-form',
    templateUrl: './knowledge-base-form.component.html',
    styleUrl: './knowledge-base-form.component.css',
    standalone: true,
    imports: [
        ReactiveFormsModule,
        MatCardModule,
        MatInputModule,
        MatChipsModule,
        MatButtonModule,
        MatIconModule,
    ]
})
export class KnowledgeBaseFormComponent {
    private fb = inject(FormBuilder);
    form = this.fb.group({
        title: ['', Validators.required],
        content: ['', Validators.required],
        keywords: [[] as string[]],
    });
    itemId: string = '';
    editMode: boolean = false;

    constructor(private knowledgeBaseService: KnowledgeBaseService, private route: ActivatedRoute,
        private router: Router,) { }

    ngOnInit(): void {
        this.route.params.subscribe(params => {
            if (params['id']) {
                this.itemId = params['id'];
                this.editMode = true;
                this.fetchItemData(this.itemId);
            }
        });
    }

    fetchItemData(itemId: string) {
        this.knowledgeBaseService.getItem(itemId).subscribe({
            next: (item) => {
                this.form.patchValue({
                    title: item.title,
                    content: item.content,
                    keywords: item.keywords,
                });
            },
            error: (error) => {
                console.error('Error fetching item data:', error);
                // Handle error, e.g., display an error message
            }
        });
    }

    onSubmit(): void {
        if (this.form.invalid) {
            return;
        }
        const formData = this.form.value as KnowledgeBaseItem;
        formData.item_id = this.itemId;
        if (this.editMode) {
            this.updateItem(formData);
        } else {
            this.createItem(formData);
        }
    }

    onCancel(): void {
        this.router.navigate(['/knowledge-base']);
    }

    createItem(itemData: KnowledgeBaseItem) {
        this.knowledgeBaseService.createItem(itemData).subscribe({
            next: () => {
                // Handle success, e.g., navigate to the item list
                this.router.navigate(['/knowledge-base']);
            },
            error: (error) => {
                console.error('Error creating item:', error);
                // Handle error
            }
        });
    }

    updateItem(itemData: KnowledgeBaseItem) {
        this.knowledgeBaseService.updateItem(this.itemId, itemData).subscribe({
            next: () => {
                // Handle success, e.g., navigate to the item list
                this.router.navigate(['/knowledge-base']);
            },
            error: (error) => {
                console.error('Error updating item:', error);
                // Handle error
            }
        });
    }

    addKeyword(event: MatChipInputEvent): void {
        const value = (event.value || '').trim();
        if (value) {
            this.form.get('keywords')?.value?.push(value);
        }
        event.chipInput.clear();
    }

    removeKeyword(keyword: string): void {
        const keywords = this.form.get('keywords')?.value as string[];
        const index = keywords.indexOf(keyword);
        if (index >= 0) {
            keywords.splice(index, 1);
        }
    }
}
