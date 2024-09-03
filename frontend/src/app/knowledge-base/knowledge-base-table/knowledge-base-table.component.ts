import { AfterViewInit, Component, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatTable, MatTableModule } from '@angular/material/table';
import { MatTableDataSourceClientSide } from '../../shared/mat-table-data-source-client-side';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatChipsModule } from '@angular/material/chips';
import { MatMenuModule } from '@angular/material/menu';
import { MatDialog } from '@angular/material/dialog';
import { SimpleDialogComponent } from '../../shared/simple-dialog/simple-dialog.component';
import { KnowledgeBaseService } from '../knowledge-base.service';

interface KnowledgeBaseItem {
    item_id: string;
    title: string;
    keywords: string[];
}

@Component({
    selector: 'app-knowledge-base-table',
    templateUrl: './knowledge-base-table.component.html',
    styleUrls: ['./knowledge-base-table.component.css'],
    standalone: true,
    imports: [
        CommonModule,
        MatToolbarModule,
        MatTableModule,
        MatPaginatorModule,
        MatSortModule,
        FormsModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatChipsModule,
        MatMenuModule,
        MatProgressSpinnerModule,
        RouterModule
    ]
})
export class KnowledgeBaseTableComponent implements AfterViewInit {
    @ViewChild(MatPaginator) paginator!: MatPaginator;
    @ViewChild(MatSort) sort!: MatSort;
    @ViewChild(MatTable) table!: MatTable<KnowledgeBaseItem>;
    dataSource: MatTableDataSourceClientSide<KnowledgeBaseItem>;

    displayedColumns: string[] = ['item_id', 'title', 'keywords', 'actions'];

    constructor(private http: HttpClient, private router: Router, public dialog: MatDialog, private knowledgeBaseService: KnowledgeBaseService) {
        this.dataSource = new MatTableDataSourceClientSide<KnowledgeBaseItem>('/api/knowledge-base');
    }

    ngAfterViewInit(): void {
        this.dataSource.sort = this.sort;
        this.dataSource.paginator = this.paginator;
        this.table.dataSource = this.dataSource;
    }

    editRow(row: KnowledgeBaseItem) {
        this.router.navigate(['knowledge-base', row.item_id, 'edit']);
    }

    viewRow(row: KnowledgeBaseItem) {
        this.router.navigate(['knowledge-base', row.item_id, 'view']);
    }

    deleteRow(row: KnowledgeBaseItem) {
        this.dialog
            .open(SimpleDialogComponent, {
                data: {
                    title: 'Confirm deletion',
                    message: `Are you sure you want to delete "<b>${row.title}</b>" item?`,
                    confirm: true
                }
            })
            .afterClosed().subscribe(result => {
                if (result && row.item_id)
                    this.knowledgeBaseService.deleteItem(row.item_id).subscribe(res => {
                        this.dataSource.data = this.dataSource.data.filter(item => item.item_id !== row.item_id);
                        this.table.renderRows();
                        this.dialog
                            .open(SimpleDialogComponent, {
                                data: {
                                    title: 'Confirmation',
                                    message: `"<b>${row.title}</b>" item has been deleted.`,
                                    confirm: false
                                }
                            });

                    });

            });
    }
}