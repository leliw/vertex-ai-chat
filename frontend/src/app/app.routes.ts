import { Routes } from '@angular/router';
import { LoginComponent } from './shared/login/login.component';
import { authGuard } from './shared/auth/auth.service';

export const routes: Routes = [
    { path: '', redirectTo: '/chat', pathMatch: 'full' },
    { path: 'login', component: LoginComponent },
    { path: 'chat', canActivate: [authGuard], loadComponent: () => import('./chat/chat.component').then(mod => mod.ChatComponent) },
    {
        path: 'knowledge-base', canActivate: [authGuard],
        loadComponent: () =>
            import('./knowledge-base/knowledge-base-page/knowledge-base-page.component')
                .then(mod => mod.KnowledgeBasePageComponent),
        children: [
            {
                path: '', canActivate: [authGuard], loadComponent: () =>
                    import('./knowledge-base/knowledge-base-table/knowledge-base-table.component')
                        .then(mod => mod.KnowledgeBaseTableComponent)
            },
            {
                path: 'create', canActivate: [authGuard], loadComponent: () =>
                    import('./knowledge-base/knowledge-base-form/knowledge-base-form.component')
                        .then(mod => mod.KnowledgeBaseFormComponent)
            },
        ]
    }
];
