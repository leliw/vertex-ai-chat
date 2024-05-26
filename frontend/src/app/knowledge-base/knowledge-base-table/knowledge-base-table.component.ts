import { AfterViewInit, Component, ViewChild } from '@angular/core';
import { MatTableModule, MatTable } from '@angular/material/table';
import { MatPaginatorModule, MatPaginator } from '@angular/material/paginator';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { KnowledgeBaseItem, KnowledgeBaseTableDataSource } from './knowledge-base-table-datasource';
import { KnowledgeBaseService } from '../knowledge-base.service';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { Router, RouterModule } from '@angular/router';
import { MatMenuModule } from '@angular/material/menu';

@Component({
    selector: 'app-knowledge-base-table',
    templateUrl: './knowledge-base-table.component.html',
    styleUrl: './knowledge-base-table.component.css',
    standalone: true,
    imports: [MatTableModule, MatPaginatorModule, MatSortModule, MatToolbarModule, MatButtonModule, MatIconModule, RouterModule, MatMenuModule],
    providers: [KnowledgeBaseService]
})
export class KnowledgeBaseTableComponent implements AfterViewInit {
    @ViewChild(MatPaginator) paginator!: MatPaginator;
    @ViewChild(MatSort) sort!: MatSort;
    @ViewChild(MatTable) table!: MatTable<KnowledgeBaseItem>;
    dataSource: KnowledgeBaseTableDataSource

    displayedColumns = ['id', 'title', 'actions'];


    constructor(private router: Router, private knowledgeBaseService: KnowledgeBaseService) {
        this.dataSource = new KnowledgeBaseTableDataSource(knowledgeBaseService);
    }

    ngAfterViewInit(): void {
        this.dataSource.sort = this.sort;
        this.dataSource.paginator = this.paginator;
        this.table.dataSource = this.dataSource;
    }

    editRow(row: KnowledgeBaseItem) {
        this.router.navigate(['knowledge-base', row.id, 'edit']);
    }

    deleteRow(row: KnowledgeBaseItem) {
        console.log('Delete row', row)
    }

}
