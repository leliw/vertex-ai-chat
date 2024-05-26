import { DataSource } from '@angular/cdk/collections';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { map } from 'rxjs/operators';
import { Observable, merge } from 'rxjs';
import { KnowledgeBaseItem, KnowledgeBaseService } from '../knowledge-base.service';


export class KnowledgeBaseTableDataSource extends DataSource<KnowledgeBaseItem> {
    data: KnowledgeBaseItem[] = [];
    paginator: MatPaginator | undefined;
    sort: MatSort | undefined;


    constructor(private knowledgeBaseService: KnowledgeBaseService) {
        super();
    }

    connect(): Observable<KnowledgeBaseItem[]> {
        if (this.paginator && this.sort) {
            // Combine everything that affects the rendered data into one update
            // stream for the data-table to consume.
            return merge(this.getData(), this.paginator.page, this.sort.sortChange)
                .pipe(map(() => {
                    return this.getPagedData(this.getSortedData([...this.data]));
                }));
        } else {
            throw Error('Please set the paginator and sort on the data source before connecting.');
        }
    }

    disconnect(): void {
        // Pass
    }

    private getData(): Observable<KnowledgeBaseItem[]> {
        return this.knowledgeBaseService.getItems()
            .pipe(map(data => { this.data = data; return data; }));
    }

    private getPagedData(data: KnowledgeBaseItem[]): KnowledgeBaseItem[] {
        if (this.paginator) {
            const startIndex = this.paginator.pageIndex * this.paginator.pageSize;
            return data.splice(startIndex, this.paginator.pageSize);
        } else {
            return data;
        }
    }

    private getSortedData(data: KnowledgeBaseItem[]): KnowledgeBaseItem[] {
        if (!this.sort?.active || this.sort.direction === '') {
            return data;
        }

        return data.sort((a, b) => {
            const isAsc = this.sort?.direction === 'asc';
            switch (this.sort?.active) {
                case 'name': return compare(a.title, b.title, isAsc);
                case 'id': return compare(a.id ?? -1, b.id ?? -1, isAsc);
                default: return 0;
            }
        });
    }
}

function compare(a: string | number, b: string | number, isAsc: boolean): number {
    return (a < b ? -1 : 1) * (isAsc ? 1 : -1);
}
export { KnowledgeBaseItem };

