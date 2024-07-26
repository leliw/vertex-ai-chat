import { Component, OnInit, ViewChild } from '@angular/core';
import { MatTableModule, MatTable, MatTableDataSource } from '@angular/material/table';
import { MatPaginatorModule, MatPaginator } from '@angular/material/paginator';
import { MatSortModule, MatSort } from '@angular/material/sort';
import { User, UserHeader, UserService } from '../user.service';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { Router, RouterModule } from '@angular/router';
import { MatMenuModule } from '@angular/material/menu';
import { SimpleDialogComponent } from '../../shared/simple-dialog/simple-dialog.component';
import { MatDialog } from '@angular/material/dialog';

@Component({
    selector: 'app-user-table',
    templateUrl: './user-table.component.html',
    standalone: true,
    imports: [MatTableModule, MatPaginatorModule, MatSortModule, MatToolbarModule, MatButtonModule, MatIconModule, RouterModule, MatMenuModule],
})
export class UserTableComponent implements OnInit {
    @ViewChild(MatPaginator) paginator!: MatPaginator;
    @ViewChild(MatSort) sort!: MatSort;
    @ViewChild(MatTable) table!: MatTable<UserHeader>;
    dataSource: MatTableDataSource<UserHeader> = new MatTableDataSource();

    displayedColumns = ['user_id', 'email', 'given_name', 'family_name', 'actions'];


    constructor(private router: Router, public dialog: MatDialog, private userService: UserService) { }

    ngOnInit(): void {
        this.userService.getUsers().subscribe(data => {
            this.dataSource = new MatTableDataSource(data);
            this.dataSource.paginator = this.paginator;
            this.dataSource.sort = this.sort;
        });
    }

    editRow(row: User) {
        this.router.navigate(['users', row.email, 'edit']);
    }

    deleteRow(row: User) {
        this.dialog
            .open(SimpleDialogComponent, {
                data: {
                    title: 'Confirm deletion',
                    message: `Are you sure you want to delete "<b>${row.email}</b>" user?`,
                    confirm: true
                }
            })
            .afterClosed().subscribe(result => {
                if (result && row.email)
                    this.userService.deleteUser(row.email).subscribe(res => {
                        this.dataSource.data = this.dataSource.data.filter(item => item.email !== row.email);
                        this.table.renderRows();
                        this.dialog
                            .open(SimpleDialogComponent, {
                                data: {
                                    title: 'Confirmation',
                                    message: `"<b>${row.email}</b>" user has been deleted.`,
                                    confirm: false
                                }
                            });

                    });

            });
    }

}

