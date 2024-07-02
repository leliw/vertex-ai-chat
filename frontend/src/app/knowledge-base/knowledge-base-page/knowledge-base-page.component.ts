import { Component, ViewChild, ViewEncapsulation, inject } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { RouterOutlet } from '@angular/router';
import { AuthService } from '../../shared/auth/auth.service';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { Observable, map, shareReplay } from 'rxjs';
import { MatIconModule } from '@angular/material/icon';
import { AsyncPipe } from '@angular/common';
import { MatSidenavContainer, MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatMenuModule } from '@angular/material/menu';
import { MatButtonModule } from '@angular/material/button';
import { MainToolbarComponent } from '../../shared/nav/main-toolbar/main-toolbar.component';

@Component({
    selector: 'app-knowledge-base-page',
    standalone: true,
    imports: [RouterOutlet, MatSidenavModule, MatListModule, MatMenuModule, MatToolbarModule, MatButtonModule, MatIconModule, AsyncPipe,
        MainToolbarComponent
    ],
    templateUrl: './knowledge-base-page.component.html',
    styleUrl: './knowledge-base-page.component.css',
    encapsulation: ViewEncapsulation.None,
})
export class KnowledgeBasePageComponent {
    @ViewChild(MatSidenavContainer) drawerContainer!: MatSidenavContainer;
    private breakpointObserver = inject(BreakpointObserver);

    isHandset$: Observable<boolean> = this.breakpointObserver.observe(Breakpoints.Handset)
        .pipe(
            map(result => result.matches),
            shareReplay()
        );
    isHandset!: boolean;

    constructor(public authService: AuthService) { }
}
