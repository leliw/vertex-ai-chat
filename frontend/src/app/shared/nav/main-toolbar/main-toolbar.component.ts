import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { AsyncPipe, CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatToolbarModule } from '@angular/material/toolbar';
import { Observable, map, shareReplay } from 'rxjs';
import { AuthService } from '../../auth/auth.service';
import { MatMenuModule } from '@angular/material/menu';
import { RouterModule } from '@angular/router';

@Component({
    selector: 'app-main-toolbar',
    standalone: true,
    imports: [
        CommonModule, AsyncPipe,
        RouterModule,
        MatToolbarModule,
        MatButtonModule, MatIconModule,
        MatMenuModule
    ],
    templateUrl: './main-toolbar.component.html',
    styleUrl: './main-toolbar.component.css'
})
export class MainToolbarComponent {
    
    @Input() drawer = true;
    @Output() drawerToggle = new EventEmitter<void>();

    private breakpointObserver = inject(BreakpointObserver);

    isHandset$: Observable<boolean> = this.breakpointObserver.observe(Breakpoints.Handset)
        .pipe(
            map(result => result.matches),
            shareReplay()
        );
    isHandset!: boolean;

    constructor(public authService: AuthService) { }
}
