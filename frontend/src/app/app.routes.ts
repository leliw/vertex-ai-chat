import { Routes } from '@angular/router';
import { LoginComponent } from './shared/login/login.component';
import { authGuard } from './shared/auth/auth.service';
import { LoginFormComponent } from './shared/auth/login-form/login-form.component';

export const routes: Routes = [
    { path: '', redirectTo: '/chat', pathMatch: 'full' },
    {
        path: 'static/terms-of-service',
        loadComponent: () =>
            import('./static/terms-of-service/terms-of-service.component')
                .then(mod => mod.TermsOfServiceComponent)
    },
    {
        path: 'static/privacy-policy',
        loadComponent: () =>
            import('./static/privacy-policy/privacy-policy.component')
                .then(mod => mod.PrivacyPolicyComponent)
    },
    // { path: 'login', component: LoginComponent },
    { path: 'login', component: LoginFormComponent },
    {
        path: 'register', canActivate: [authGuard],
        loadComponent: () =>
            import('./register/register.component')
                .then(mod => mod.RegisterComponent)
    },
    {
        path: 'reset-password-request',
        loadComponent: () => import('./shared/auth/reset-password-request-form/reset-password-request-form.component').then(mod => mod.ResetPasswordRequestFormComponent)
    },
    {
        path: 'reset-password',
        loadComponent: () => import('./shared/auth/reset-password-form/reset-password-form.component').then(mod => mod.ResetPasswordFormComponent)
    },
    {
        path: 'chat', canActivate: [authGuard],
        loadComponent: () =>
            import('./chat/chat-page/chat-page.component')
                .then(mod => mod.ChatPageComponent)
    },
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
            {
                path: ':id/edit', canActivate: [authGuard], loadComponent: () =>
                    import('./knowledge-base/knowledge-base-form/knowledge-base-form.component')
                        .then(mod => mod.KnowledgeBaseFormComponent)
            },
            {
                path: ':id/view', canActivate: [authGuard], loadComponent: () =>
                    import('./knowledge-base/knowledge-base-view/knowledge-base-view.component')
                        .then(mod => mod.KnowledgeBaseViewComponent)
            },
        ]
    },
    {
        path: 'agents', canActivate: [authGuard],
        loadComponent: () =>
            import('./agent/agent-page/agent-page.component')
                .then(mod => mod.AgentPageComponent),
        children: [
            {
                path: '', canActivate: [authGuard], loadComponent: () =>
                    import('./agent/agent-table/agent-table.component')
                        .then(mod => mod.AgentTableComponent)
            },
            {
                path: 'create', canActivate: [authGuard], loadComponent: () =>
                    import('./agent/agent-form/agent-form.component')
                        .then(mod => mod.AgentFormComponent)
            },
            {
                path: ':id/edit', canActivate: [authGuard], loadComponent: () =>
                    import('./agent/agent-form/agent-form.component')
                        .then(mod => mod.AgentFormComponent)
            },
        ]
    },
    {
        path: 'users', canActivate: [authGuard],
        loadComponent: () =>
            import('./user/user-page/user-page.component')
                .then(mod => mod.UserPageComponent),
        children: [
            {
                path: '', canActivate: [authGuard], loadComponent: () =>
                    import('./user/user-table/user-table.component')
                        .then(mod => mod.UserTableComponent)
            },
            {
                path: ':email/edit', canActivate: [authGuard], loadComponent: () =>
                    import('./user/user-form/user-form.component')
                        .then(mod => mod.UserFormComponent)
            },
        ]
    }
];


