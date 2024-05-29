import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface KnowledgeBaseItemHeader {
    item_id: string | undefined;
    title: string;
    keywords: string[] | undefined;
}

export interface KnowledgeBaseItem extends KnowledgeBaseItemHeader {
    content: string;
    metadata: { [key: string]: string } | undefined;
}

@Injectable({
    providedIn: 'root'
})
export class KnowledgeBaseService {
    private apiUrl = '/api/knowledge-base';

    constructor(private http: HttpClient) { }

    // Create a new knowledge base item
    createItem(item: KnowledgeBaseItem): Observable<KnowledgeBaseItem> {
        return this.http.post<KnowledgeBaseItem>(this.apiUrl, item);
    }

    // Get a knowledge base item by ID
    getItem(itemId: string): Observable<KnowledgeBaseItem> {
        return this.http.get<KnowledgeBaseItem>(`${this.apiUrl}/${itemId}`);
    }

    // Get all knowledge base items
    getItems(): Observable<KnowledgeBaseItemHeader[]> {
        return this.http.get<KnowledgeBaseItemHeader[]>(this.apiUrl);
    }

    // Update a knowledge base item
    updateItem(itemId: string, updatedItem: KnowledgeBaseItem): Observable<KnowledgeBaseItem> {
        return this.http.put<KnowledgeBaseItem>(`${this.apiUrl}/${itemId}`, updatedItem);
    }

    // Delete a knowledge base item
    deleteItem(itemId: string): Observable<boolean> {
        return this.http.delete<boolean>(`${this.apiUrl}/${itemId}`);
    }
}