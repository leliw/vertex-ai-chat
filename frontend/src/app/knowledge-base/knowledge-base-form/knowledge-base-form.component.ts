import { Component, inject } from '@angular/core';

import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatRadioModule } from '@angular/material/radio';
import { MatCardModule } from '@angular/material/card';
import { KnowledgeBaseItem, KnowledgeBaseService } from '../knowledge-base.service';
import { ActivatedRoute, Router } from '@angular/router';


@Component({
    selector: 'app-knowledge-base-form',
    templateUrl: './knowledge-base-form.component.html',
    styleUrl: './knowledge-base-form.component.css',
    standalone: true,
    imports: [
        MatInputModule,
        MatButtonModule,
        MatSelectModule,
        MatRadioModule,
        MatCardModule,
        ReactiveFormsModule
    ]
})
export class KnowledgeBaseFormComponent {
    private fb = inject(FormBuilder);
    form = this.fb.group({
        title: ['', Validators.required],
        content: ['', Validators.required],
        keywords: [''],
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
                    keywords: item?.keywords ? item.keywords.join(', ') : '',
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
        const formData = this.form.value as unknown as KnowledgeBaseItem;
        // formData.id = this.itemId;
        // Split keywords string into an array
        formData.keywords = this.form.value.keywords ? this.form.value.keywords.split(',').map((keyword: string) => keyword.trim()) : [];
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

}
