import { waitForAsync, ComponentFixture, TestBed } from '@angular/core/testing';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

import { KnowledgeBaseFormComponent } from './knowledge-base-form.component';

describe('KnowledgeBaseFormComponent', () => {
  let component: KnowledgeBaseFormComponent;
  let fixture: ComponentFixture<KnowledgeBaseFormComponent>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [NoopAnimationsModule]
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(KnowledgeBaseFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should compile', () => {
    expect(component).toBeTruthy();
  });
});
