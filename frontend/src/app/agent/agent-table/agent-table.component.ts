import { Component, OnInit, ViewChild } from '@angular/core';
import { MatTableModule, MatTable, MatTableDataSource } from '@angular/material/table';
import { MatPaginatorModule, MatPaginator } from '@angular/material/paginator';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { Agent, AgentService } from '../agent.service';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { Router, RouterModule } from '@angular/router';
import { MatMenuModule } from '@angular/material/menu';
import { SimpleDialogComponent } from '../../shared/simple-dialog/simple-dialog.component';
import { MatDialog } from '@angular/material/dialog';
import { MatChipsModule } from '@angular/material/chips';

@Component({
    selector: 'app-agent-table',
    templateUrl: './agent-table.component.html',
    styleUrl: './agent-table.component.css',
    standalone: true,
    imports: [
        RouterModule,
        MatTableModule, 
        MatPaginatorModule, 
        MatSortModule,
        MatToolbarModule,
        MatMenuModule,
        MatButtonModule, 
        MatIconModule,
        MatChipsModule,
    ],
    providers: [AgentService]
})
export class AgentTableComponent implements OnInit {
    @ViewChild(MatPaginator) paginator!: MatPaginator;
    @ViewChild(MatSort) sort!: MatSort;
    @ViewChild(MatTable) table!: MatTable<string>;
    dataSource: MatTableDataSource<Agent> = new MatTableDataSource();

    displayedColumns = ['name', 'ai_model_name', 'keywords', 'actions'];


    constructor(private router: Router, public dialog: MatDialog, private agentService: AgentService) { }

    ngOnInit(): void {
        this.agentService.get_all().subscribe(data => {
            this.dataSource = new MatTableDataSource(data);
            this.dataSource.paginator = this.paginator;
            this.dataSource.sort = this.sort;
        });
    }

    editRow(row: Agent) {
        this.router.navigate(['agents', row.name, 'edit']);
    }

    deleteRow(row: Agent) {
        this.dialog
            .open(SimpleDialogComponent, {
                data: {
                    title: 'Confirm deletion',
                    message: `Are you sure you want to delete "<b>${row.name}</b>" agent?`,
                    confirm: true
                }
            })
            .afterClosed().subscribe(result => {
                if (result)
                    this.agentService.delete(row.name).subscribe(res => {
                        this.dataSource.data = this.dataSource.data.filter(item => item !== row);
                        this.table.renderRows();
                        this.dialog
                            .open(SimpleDialogComponent, {
                                data: {
                                    title: 'Confirmation',
                                    message: `"<b>${row.name}</b>" agent has been deleted.`,
                                    confirm: false
                                }
                            });

                    });

            });
    }

}

