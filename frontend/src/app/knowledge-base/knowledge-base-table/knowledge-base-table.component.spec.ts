import { waitForAsync, ComponentFixture, TestBed } from '@angular/core/testing';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

import { KnowledgeBaseTableComponent } from './knowledge-base-table.component';

describe('KnowledgeBaseTableComponent', () => {
  let component: KnowledgeBaseTableComponent;
  let fixture: ComponentFixture<KnowledgeBaseTableComponent>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      imports: [NoopAnimationsModule]
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(KnowledgeBaseTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should compile', () => {
    expect(component).toBeTruthy();
  });
});
