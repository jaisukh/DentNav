export type QuestionType = "textarea" | "dropdown" | "radio" | "multiSelect" | "searchableDropdown";

export type QuestionBase = {
  id: string;
  order: number;
  type: QuestionType;
  label: string;
  description?: string;
};

export type QuestionDependsOn = {
  questionId: string;
  /** Reserved for future S3-driven wiring; resolution uses `questionId` + degreesByCountry. */
  optionsFrom: string;
};

export type TextareaQuestion = QuestionBase & {
  type: "textarea";
  placeholder?: string;
  rows?: number;
};

export type SearchableDropdownQuestion = QuestionBase & {
  type: "searchableDropdown";
  placeholder?: string;
  optionsFrom: "keys:degreesByCountry" | string;
};

export type DropdownQuestion = QuestionBase & {
  type: "dropdown";
  placeholder?: string;
  /** Static options when no dependency. */
  options?: string[];
  dependsOn?: QuestionDependsOn;
};

export type RadioQuestion = QuestionBase & {
  type: "radio";
  options: string[];
};

export type MultiSelectQuestion = QuestionBase & {
  type: "multiSelect";
  placeholder?: string;
  options: string[];
  minSelections?: number;
  maxSelections?: number;
};

export type Question =
  | TextareaQuestion
  | DropdownQuestion
  | RadioQuestion
  | MultiSelectQuestion
  | SearchableDropdownQuestion;

export type QuestionnaireMeta = {
  title: string;
  description: string;
};

export type QuestionnaireDocument = {
  version: string;
  lastUpdated: string;
  meta: QuestionnaireMeta;
  degreesByCountry: Record<string, string[]>;
  questions: Question[];
};

export type AnswerValue = string | string[];
