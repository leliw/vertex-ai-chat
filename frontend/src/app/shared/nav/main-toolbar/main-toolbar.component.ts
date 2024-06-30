import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { AsyncPipe } from '@angular/common';
import { Component, EventEmitter, Output, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatToolbarModule } from '@angular/material/toolbar';
import { Observable, map, shareReplay } from 'rxjs';
import { AuthService } from '../../auth/auth.service';

@Component({
    selector: 'app-main-toolbar',
    standalone: true,
    imports: [
        AsyncPipe,
        MatToolbarModule,
        MatButtonModule, MatIconModule,
    ],
    templateUrl: './main-toolbar.component.html',
    styleUrl: './main-toolbar.component.css'
})
export class MainToolbarComponent {

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
