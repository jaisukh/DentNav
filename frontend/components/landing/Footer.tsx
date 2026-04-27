import { BrandLogo } from "./BrandLogo";
import { QuestionnaireLink } from "@/components/questionnaire/QuestionnaireLink";

export function Footer() {
  return (
    <footer className="border-t border-[#E2E8F0] bg-white">
      <div className="page-shell py-10">
        <div className="flex w-full flex-col justify-between gap-12 lg:flex-row lg:gap-8">
          <div className="w-full shrink-0 lg:max-w-md">
            <BrandLogo iconSize={42} textClassName="font-bold text-[#1B3A5C]" />
            <p className="mt-6 max-w-[384px] text-sm font-normal leading-[23px] text-[#64748B]">
              The definitive resource for international dentists seeking license
              and practice in the United States. Expertise at every step.
            </p>
            <div className="mt-8">
              <QuestionnaireLink
                className="inline-flex items-center justify-center rounded-full bg-dent-ink px-8 py-3.5 text-sm font-bold text-white transition-all hover:bg-dent-deep active:scale-95"
              >
                Get Started
              </QuestionnaireLink>
            </div>
          </div>

          <div className="grid w-full grid-cols-1 gap-10 sm:grid-cols-2 sm:gap-x-12 lg:w-auto">
            <div className="space-y-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-dent-ink">
                Contact
              </h3>
              <div className="space-y-3 text-sm font-medium text-[#64748B]">
                <p>DentNav, Seattle, Washington, USA</p>
                <p className="text-dent-deep font-bold">+91 40 1234 5678</p>
                <p>support@dentnav.com</p>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-dent-ink">
                Hours
              </h3>
              <div className="space-y-3 text-sm font-medium text-[#64748B]">
                <p>Monday—Friday</p>
                <p>9am - 6pm (PST)</p>
              </div>
              <div className="flex gap-4 pt-4">
                <a href="#" className="text-[#94A3B8] transition-colors hover:text-dent-deep" aria-label="Instagram">
                  <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
                  </svg>
                </a>
                <a href="#" className="text-[#94A3B8] transition-colors hover:text-dent-deep" aria-label="Facebook">
                  <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M22.675 0h-21.35c-.732 0-1.325.593-1.325 1.325v21.351c0 .731.593 1.324 1.325 1.324h11.495v-8.74h-2.94v-3.403h2.94v-2.511c0-2.915 1.78-4.502 4.379-4.502 1.244 0 2.315.093 2.627.135v3.046h-1.803c-1.414 0-1.688.672-1.688 1.658v2.171h3.374l-.439 3.403h-2.935v8.74h6.136c.731 0 1.324-.593 1.324-1.325v-21.35c0-.732-.593-1.325-1.325-1.325z" />
                  </svg>
                </a>
                <a href="#" className="text-[#94A3B8] transition-colors hover:text-dent-deep" aria-label="LinkedIn">
                  <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-1.337-.025-3.059-1.865-3.059-1.865 0-2.15 1.458-2.15 2.962v5.701h-3v-11h2.878v1.502h.041c.4-.758 1.378-1.554 2.83-1.554 3.028 0 3.591 1.993 3.591 4.584v6.914z" />
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 flex w-full flex-col gap-4 border-t border-[#F1F5F9] pt-8 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm font-normal leading-5 text-[#94A3B8]">
            © {new Date().getFullYear()} DentNav. All rights reserved.
          </p>
          <div className="flex gap-8 text-sm font-medium leading-5 text-[#64748B]">
            <a href="#" className="hover:text-dent-ink transition-colors">
              Privacy Policy
            </a>
            <a href="#" className="hover:text-dent-ink transition-colors">
              Terms & Conditions
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
