export type QuestionType = "textarea" | "dropdown" | "radio" | "multiSelect";

export type QuestionBase = {
  id: string;
  order: number;
  type: QuestionType;
  label: string;
  description?: string;
};

export type TextareaQuestion = QuestionBase & {
  type: "textarea";
  placeholder?: string;
  /** Visual height hint; defaults to 3 rows if omitted */
  rows?: number;
};

export type DropdownQuestion = QuestionBase & {
  type: "dropdown";
  placeholder?: string;
  options: string[];
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
  | MultiSelectQuestion;

export type QuestionnaireDocument = {
  id: string;
  title: string;
  subtitle: string;
  questions: Question[];
};

export type AnswerValue = string | string[];
