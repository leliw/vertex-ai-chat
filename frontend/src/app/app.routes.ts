import { Routes } from '@angular/router';
import { ChatComponent } from './chat/chat.component';
import { LoginComponent } from './shared/login/login.component';
import { authGuard } from './shared/auth/auth.service';

export const routes: Routes = [
    { path: '', redirectTo: '/chat', pathMatch: 'full' },
    { path: 'login', component: LoginComponent },
    { path: 'chat', component: ChatComponent, canActivate: [authGuard] },
];
