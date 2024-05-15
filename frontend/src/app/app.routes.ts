import { Routes } from '@angular/router';
import { LoginComponent } from './shared/login/login.component';
import { authGuard } from './shared/auth/auth.service';

export const routes: Routes = [
    { path: '', redirectTo: '/chat', pathMatch: 'full' },
    { path: 'login', component: LoginComponent },
    { path: 'chat', canActivate: [authGuard], loadComponent: () => import('./chat/chat.component').then(mod => mod.ChatComponent) },
];
