import { Component, ViewEncapsulation } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MainToolbarComponent } from '../../shared/nav/main-toolbar/main-toolbar.component';

@Component({
    selector: 'app-knowledge-base-page',
    standalone: true,
    imports: [RouterOutlet, MainToolbarComponent],
    templateUrl: './knowledge-base-page.component.html',
    styleUrl: './knowledge-base-page.component.css',
    encapsulation: ViewEncapsulation.None,
})
export class KnowledgeBasePageComponent {

    constructor() { }

}
