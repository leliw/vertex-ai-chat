import { Component, OnInit, ViewChild } from '@angular/core';
import { MatTableModule, MatTable, MatTableDataSource } from '@angular/material/table';
import { MatPaginatorModule, MatPaginator } from '@angular/material/paginator';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { KnowledgeBaseItem, KnowledgeBaseService } from '../knowledge-base.service';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { Router, RouterModule } from '@angular/router';
import { MatMenuModule } from '@angular/material/menu';
import { SimpleDialogComponent } from '../../shared/simple-dialog/simple-dialog.component';
import { MatDialog } from '@angular/material/dialog';

@Component({
    selector: 'app-knowledge-base-table',
    templateUrl: './knowledge-base-table.component.html',
    styleUrl: './knowledge-base-table.component.css',
    standalone: true,
    imports: [MatTableModule, MatPaginatorModule, MatSortModule, MatToolbarModule, MatButtonModule, MatIconModule, RouterModule, MatMenuModule],
    providers: [KnowledgeBaseService]
})
export class KnowledgeBaseTableComponent implements OnInit {
    @ViewChild(MatPaginator) paginator!: MatPaginator;
    @ViewChild(MatSort) sort!: MatSort;
    @ViewChild(MatTable) table!: MatTable<KnowledgeBaseItem>;
    dataSource: MatTableDataSource<KnowledgeBaseItem> = new MatTableDataSource();

    displayedColumns = ['id', 'title', 'actions'];


    constructor(private router: Router, public dialog: MatDialog, private knowledgeBaseService: KnowledgeBaseService) { }

    ngOnInit(): void {
        this.knowledgeBaseService.getItems().subscribe(data => {
            this.dataSource = new MatTableDataSource(data);
            this.dataSource.paginator = this.paginator;
            this.dataSource.sort = this.sort;
        });
    }

    editRow(row: KnowledgeBaseItem) {
        this.router.navigate(['knowledge-base', row.id, 'edit']);
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
                if (result && row.id)
                    this.knowledgeBaseService.deleteItem(row.id).subscribe(res => {
                        console.log(this.dataSource.data);
                        this.dataSource.data = this.dataSource.data.filter(item => item.id !== row.id);
                        console.log(this.dataSource.data);
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
