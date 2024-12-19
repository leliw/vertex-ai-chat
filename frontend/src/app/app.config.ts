import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';

import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { GoogleLoginProvider, SocialAuthServiceConfig } from '@abacritt/angularx-social-login';
import { authInterceptor } from './shared/auth/auth.service'
import { ConfigService } from './shared/config/config.service';

export const appConfig: ApplicationConfig = {
    providers: [
        provideRouter(routes),
        provideAnimationsAsync(),
        provideHttpClient(withInterceptors([authInterceptor])),
        {
            provide: 'SocialAuthServiceConfig',
            useFactory: async (configService: ConfigService) => {
                const clientId = await configService.getOAuthClientId();
                const oneTapEnabled = localStorage.getItem("user") == null;
                return {
                    autoLogin: false,
                    providers: [
                        {
                            id: GoogleLoginProvider.PROVIDER_ID,
                            provider: new GoogleLoginProvider(clientId, { oneTapEnabled: oneTapEnabled })
                        }
                    ],
                    onError: (err: any) => {
                        console.error(err);
                    }
                } as SocialAuthServiceConfig;
            },
            deps: [ConfigService]
        }
    ]
};
