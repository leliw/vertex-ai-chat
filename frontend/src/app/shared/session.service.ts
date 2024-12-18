import { HttpClient, HttpEventType } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';

export interface FileHeader {
    name: string;
    mime_type: string;
}

@Injectable({
    providedIn: 'root'
})
export class SessionService {

    selectedFiles: File[] = [];
    uploadProgress: number[] = [];
    isUploading$: BehaviorSubject<boolean> = new BehaviorSubject(false);

    constructor(private httpClient: HttpClient) { }

    deleteFile(filename: string): Observable<void> {
        return this.httpClient.delete<void>(`/api/files/${filename}`);
    }

    clearFiles(): void {
        this.selectedFiles = [];
        this.uploadProgress = [];
    }

    getAllFiles(): Observable<FileHeader[]> {
        return this.httpClient.get<FileHeader[]>(`/api/files`).pipe(
            tap(files => {
                this.selectedFiles = files.map(file => new File([], file.name));
                this.uploadProgress = files.map(() => 100);
            })
        );
    }

    openFileDialog(): void {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.click();
        input.onchange = (event: any) => this.uploadFiles(event.target.files)
    }

    onFileSelected(event: any): void {
        this.uploadFiles(event.target.files);
    }

    onFileDropped(event: DragEvent): void {
        event.preventDefault();
        if (event.dataTransfer?.files)
            this.uploadFiles(event.dataTransfer.files);
    }

    removeFile(index: number): void {
        const fileName = this.selectedFiles[index].name;
        this.deleteFile(fileName).subscribe(() => this.selectedFiles.splice(index, 1));
        this.uploadProgress.splice(index, 1)
    }

    uploadFiles(files: FileList, index: number = 0, offset: number = -1) {
        if (offset == -1)
            offset = this.selectedFiles.length;
        if (index == 0) {
            this.isUploading$.next(true);
            Array.from(files).forEach(file => this.selectedFiles.push(file));
        }
        if (index >= files.length) {
            this.isUploading$.next(false);
            return;
        }
        const file = files[index];
        const formData = new FormData();
        formData.append('files', file);

        this.httpClient.post<void>(`/api/files`, formData, {
            reportProgress: true,
            observe: 'events'
        }).subscribe({
            next: event => {
                if (event.type === HttpEventType.UploadProgress && event.total) {
                    this.uploadProgress[offset + index] = Math.round(10 * event.loaded / event.total) * 10;
                }
            },
            complete: () => {
                this.uploadProgress[offset + index] = 100;
                this.uploadFiles(files, index + 1, offset);
            }
        });
    }

}
