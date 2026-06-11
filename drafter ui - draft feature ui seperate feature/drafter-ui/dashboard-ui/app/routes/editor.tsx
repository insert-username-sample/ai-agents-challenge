import { useState } from "react";
import Sidebar, { ClauselyLogo } from "~/components/Sidebar";
import ClauselyAIPanel from "~/components/ClauselyAIPanel";
import {
  ChevronDown,
  Save,
  Undo2,
  Redo2,
  HelpCircle,
  Bell,
  ChevronRight,
  Maximize2,
  Minus,
  Plus,
  Play,
  RotateCcw,
  Search,
  MessageSquare,
  Sparkles,
  Scale,
  FolderOpen,
  Settings,
  Mic,
  AudioLines,
  Link as LinkIcon,
  ExternalLink,
  ChevronLeft,
  X,
  FileText,
  AlignLeft,
  Bold,
  Italic,
  Underline,
  Strikethrough,
  List,
  ListOrdered,
  Grid,
} from "lucide-react";
import { Link } from "@remix-run/react";

type AnnotationKey = "petition" | "petitioner" | "ministry" | "article";

export default function DocumentEditor() {
  const [activeAnnotation, setActiveAnnotation] = useState<AnnotationKey | null>(null);
  const [zoom, setZoom] = useState(100);
  const [askText, setAskText] = useState("");

  const outline = [
    { label: "1. Title Page", active: true },
    { label: "2. Index", active: false },
    { label: "3. Synopsis", active: false },
    { label: "4. List of Dates", active: false },
    {
      label: "5. Parties",
      active: false,
      children: [{ label: "5.1 Petitioner(s)" }, { label: "5.2 Respondent(s)" }],
    },
    { label: "6. Facts of the Case", active: false },
    {
      label: "7. Grounds",
      active: false,
      children: [{ label: "7.1 Ground I" }, { label: "7.2 Ground II" }, { label: "7.3 Ground III" }],
    },
    { label: "8. Interim Relief", active: false },
    { label: "9. Prayer", active: false },
    { label: "10. Verification", active: false },
    {
      label: "11. Annexures",
      active: false,
      children: [{ label: "11.1 Annexure A" }, { label: "11.2 Annexure B" }],
    },
  ];

  const handleAnnotationClick = (key: AnnotationKey, e: React.MouseEvent) => {
    e.stopPropagation();
    setActiveAnnotation(activeAnnotation === key ? null : key);
  };

  const closeAnnotation = () => setActiveAnnotation(null);

  return (
    <div className="flex h-screen bg-[#F8F9FA] text-[#111827] overflow-hidden font-sans select-none" onClick={closeAnnotation}>
      {/* Sidebar: Icon Bar + Outline Sidebar (Left) */}
      <div className="flex h-full bg-white border-r border-[#E5E7EB] z-20">
        {/* Leftmost Mini Navigation Bar (Sidebar icons matching visual 1:1) */}
        <div className="w-14 bg-white border-r border-[#E5E7EB]/60 flex flex-col items-center justify-between py-4">
          <div className="flex flex-col items-center gap-5.5 w-full">
            <Link to="/">
              <ClauselyLogo className="w-7 h-7 text-[#2563EB]" />
            </Link>
            <Link to="/" className="p-2 text-[#6B7280] hover:text-[#2563EB] rounded-lg transition-colors">
              <FileText className="w-5 h-5" />
            </Link>
            <button className="p-2 text-[#6B7280] hover:text-[#2563EB] rounded-lg transition-colors">
              <Search className="w-5 h-5" />
            </button>
            <button className="p-2 text-[#6B7280] hover:text-[#2563EB] rounded-lg transition-colors">
              <MessageSquare className="w-5 h-5" />
            </button>
            <button className="p-2 text-[#6B7280] hover:text-[#2563EB] rounded-lg transition-colors">
              <Sparkles className="w-5 h-5 text-[#2563EB]" />
            </button>
            <button className="p-2 text-[#6B7280] hover:text-[#2563EB] rounded-lg transition-colors">
              <Scale className="w-5 h-5" />
            </button>
            <button className="p-2 text-[#6B7280] hover:text-[#2563EB] rounded-lg transition-colors">
              <FolderOpen className="w-5 h-5" />
            </button>
          </div>
          <button className="p-2 text-[#6B7280] hover:text-[#2563EB] rounded-lg transition-colors">
            <Settings className="w-5 h-5" />
          </button>
        </div>

        {/* Outline List (Left sidebar expansion) */}
        <div className="w-[200px] flex flex-col justify-between h-full bg-[#FFFFFF] p-4 overflow-y-auto border-r border-[#E5E7EB]/40">
          <div className="space-y-4 text-left">
            <div className="flex items-center justify-between select-none">
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#111827]">
                Document
              </span>
              <button className="text-[#6B7280] hover:text-[#111827]">
                <Plus className="w-4 h-4" />
              </button>
            </div>

            {/* Navigation Outline Nodes */}
            <div className="space-y-1">
              {outline.map((item) => (
                <div key={item.label}>
                  <div
                    className={`flex items-center gap-1.5 px-2 py-1.5 rounded-lg text-xs font-semibold select-none cursor-pointer transition-colors ${
                      item.active
                        ? "bg-[#EFF6FF] text-[#2563EB]"
                        : "text-[#6B7280] hover:bg-[#F8F9FA] hover:text-[#111827]"
                    }`}
                  >
                    {item.children && <ChevronDown className="w-3 h-3 text-[#6B7280]" />}
                    <span className="truncate">{item.label}</span>
                  </div>
                  {item.children && (
                    <div className="pl-4 mt-0.5 space-y-0.5">
                      {item.children.map((child) => (
                        <div
                          key={child.label}
                          className="px-2 py-1 text-[11px] font-medium text-[#6B7280] hover:text-[#111827] rounded-lg cursor-pointer transition-colors"
                        >
                          {child.label}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Editor Center Container (Top Bar + Ribbon + Ruler + Sheet) */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        {/* Document Top Bar */}
        <header className="h-12 border-b border-[#E5E7EB] bg-white px-5 flex items-center justify-between select-none">
          <div className="flex items-center gap-4.5">
            <Link
              to="/"
              className="p-1.5 rounded-lg text-[#6B7280] hover:bg-[#F8F9FA] hover:text-[#111827] transition-all"
            >
              <ChevronLeft className="w-4.5 h-4.5" />
            </Link>
            <div className="flex items-center gap-2">
              <Save className="w-4 h-4 text-[#6B7280] cursor-pointer hover:text-[#111827]" />
              <Undo2 className="w-4 h-4 text-[#6B7280] cursor-pointer hover:text-[#111827]" />
              <Redo2 className="w-4 h-4 text-[#6B7280] cursor-pointer hover:text-[#111827]" />
            </div>

            {/* Document Title Menu */}
            <div className="relative flex items-center gap-1 cursor-pointer group">
              <span className="text-xs font-bold text-[#111827] hover:text-[#2563EB] transition-colors">
                Writ Petition (Civil) No. 2456 of 2024.docx
              </span>
              <ChevronDown className="w-3.5 h-3.5 text-[#6B7280] group-hover:text-[#2563EB] transition-colors" />
            </div>

            {/* Saved Indicator */}
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#16A34A] animate-pulse"></span>
              <span className="text-[10px] font-bold text-[#16A34A] uppercase tracking-wider">
                Saved
              </span>
            </div>
          </div>

          {/* Right Header Controls */}
          <div className="flex items-center gap-3">
            <HelpCircle className="w-4.5 h-4.5 text-[#6B7280] cursor-pointer hover:text-[#111827]" />
            <div className="relative">
              <Bell className="w-4.5 h-4.5 text-[#6B7280] cursor-pointer hover:text-[#111827]" />
              <span className="absolute top-[-3px] right-[-3px] w-2.5 h-2.5 rounded-full bg-[#EA580C] border-2 border-white"></span>
            </div>
            <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center text-white text-[11px] font-bold shadow-sm select-none">
              MK
            </div>
            <span className="text-xs font-bold text-[#111827] hidden sm:inline-block">
              Adv. Manas Khobrekar
            </span>
          </div>
        </header>

        {/* Microsoft Word Style Ribbon Toolbar (Rich Options matching image.png 1:1) */}
        <div className="bg-[#FFFFFF] border-b border-[#E5E7EB] px-5 py-2.5 flex flex-wrap items-center gap-6 select-none text-left shadow-xs">
          {/* Ribbon Tabs Row */}
          <div className="w-full flex items-center border-b border-[#E5E7EB]/40 pb-2 mb-2 gap-5.5">
            {["File", "Home", "Insert", "Draw", "Layout", "References", "Review", "View"].map(
              (tab, idx) => (
                <button
                  key={tab}
                  className={`text-xs font-bold transition-all ${
                    idx === 1
                      ? "text-[#2563EB] border-b-2 border-[#2563EB] pb-0.5"
                      : "text-[#6B7280] hover:text-[#111827]"
                  }`}
                >
                  {tab}
                </button>
              )
            )}
            <button className="text-xs font-extrabold text-[#2563EB] hover:text-[#1d4ed8] flex items-center gap-0.5">
              <span>Clausely AI</span>
              <Sparkles className="w-3.5 h-3.5 fill-[#2563EB]/10" />
            </button>
          </div>

          {/* Ribbon Toolbar Actions Grid */}
          <div className="flex flex-wrap items-center gap-4.5 select-none text-[#6B7280]">
            {/* Group 1: Clipboard */}
            <div className="flex items-center gap-1.5 border-r border-[#E5E7EB] pr-4.5">
              <span className="text-[10px] font-extrabold uppercase text-[#6B7280] mr-2">Font</span>
              <select className="text-xs font-semibold bg-[#F8F9FA] border border-[#E5E7EB] px-2.5 py-1.5 rounded-md appearance-none outline-none cursor-pointer">
                <option>Times New Roman</option>
                <option>Arial</option>
                <option>Inter</option>
              </select>
              <select className="text-xs font-semibold bg-[#F8F9FA] border border-[#E5E7EB] px-2.5 py-1.5 rounded-md appearance-none outline-none cursor-pointer w-14">
                <option>12</option>
                <option>14</option>
                <option>16</option>
              </select>
            </div>

            {/* Group 2: Typography Style modifiers */}
            <div className="flex items-center gap-1.5 border-r border-[#E5E7EB] pr-4.5">
              <button className="p-1.5 rounded-md hover:bg-[#F8F9FA] hover:text-[#111827] active:scale-95 transition-all">
                <Bold className="w-4 h-4" />
              </button>
              <button className="p-1.5 rounded-md hover:bg-[#F8F9FA] hover:text-[#111827] active:scale-95 transition-all">
                <Italic className="w-4 h-4" />
              </button>
              <button className="p-1.5 rounded-md hover:bg-[#F8F9FA] hover:text-[#111827] active:scale-95 transition-all">
                <Underline className="w-4 h-4" />
              </button>
              <button className="p-1.5 rounded-md hover:bg-[#F8F9FA] hover:text-[#111827] active:scale-95 transition-all">
                <Strikethrough className="w-4 h-4" />
              </button>
            </div>

            {/* Group 3: Paragraph alignment & listing */}
            <div className="flex items-center gap-1.5 border-r border-[#E5E7EB] pr-4.5">
              <button className="p-1.5 rounded-md hover:bg-[#F8F9FA] hover:text-[#111827]">
                <AlignLeft className="w-4 h-4" />
              </button>
              <button className="p-1.5 rounded-md hover:bg-[#F8F9FA] hover:text-[#111827]">
                <List className="w-4 h-4" />
              </button>
              <button className="p-1.5 rounded-md hover:bg-[#F8F9FA] hover:text-[#111827]">
                <ListOrdered className="w-4 h-4" />
              </button>
            </div>

            {/* Group 4: Quick Styles Normal/Heading */}
            <div className="flex items-center gap-2">
              <div className="border border-[#2563EB] bg-[#EFF6FF] text-[#2563EB] px-3.5 py-1 rounded-md text-xs font-bold shadow-xs select-none">
                Normal
              </div>
              <div className="border border-[#E5E7EB] hover:bg-[#F8F9FA] text-[#6B7280] hover:text-[#111827] px-3.5 py-1 rounded-md text-xs font-bold shadow-xs cursor-pointer select-none">
                Heading 1
              </div>
              <div className="border border-[#E5E7EB] hover:bg-[#F8F9FA] text-[#6B7280] hover:text-[#111827] px-3.5 py-1 rounded-md text-xs font-bold shadow-xs cursor-pointer select-none">
                Heading 2
              </div>
            </div>
          </div>
        </div>

        {/* Ruler Bar */}
        <div className="h-6 bg-[#F8F9FA] border-b border-[#E5E7EB] px-[120px] flex items-center relative select-none">
          <div className="w-full h-[1px] bg-[#E5E7EB]"></div>
          {/* Mock ruler markers */}
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15].map((num) => (
            <div
              key={num}
              className="absolute text-[8px] font-extrabold text-[#6B7280]/70 select-none pointer-events-none"
              style={{ left: `${120 + num * 45}px` }}
            >
              <span>{num}</span>
              <div className="h-1.5 w-[1px] bg-[#E5E7EB] mx-auto mt-0.5"></div>
            </div>
          ))}
        </div>

        {/* Scrollable Document Area wrapper */}
        <div className="flex-1 overflow-y-auto p-8 relative flex justify-center bg-[#F8F9FA]">
          {/* Main Visual A4 Page */}
          <div className="w-[812px] min-h-[1100px] h-fit bg-white border border-[#E5E7EB] shadow-lg rounded-sm px-16 py-20 relative text-left font-serif leading-relaxed text-sm select-text">
            {/* Annotation Popovers (Aesthetic absolute positions) */}
            
            {/* 1. Writ Petition Number Annotation Popover */}
            {activeAnnotation === "petition" && (
              <div
                className="absolute bg-white border border-[#E5E7EB] rounded-xl p-4.5 shadow-xl w-[260px] z-50 text-left"
                style={{ top: "185px", left: "420px" }}
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between border-b border-[#E5E7EB]/40 pb-2 mb-2">
                  <span className="text-xs font-bold text-[#111827]">Writ Petition Number</span>
                  <button onClick={closeAnnotation} className="text-[#6B7280] hover:text-[#111827]">
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
                <p className="text-[11px] text-[#6B7280] font-medium leading-relaxed mb-3">
                  Unique identifier for this petition filed in Bombay High Court.
                </p>
                <button className="text-[10px] font-bold text-[#2563EB] hover:text-[#1d4ed8] transition-colors flex items-center gap-0.5">
                  <span>Click to view case details</span>
                </button>
              </div>
            )}

            {/* 2. Petitioner Annotation Popover */}
            {activeAnnotation === "petitioner" && (
              <div
                className="absolute bg-white border border-[#E5E7EB] rounded-xl p-4.5 shadow-xl w-[260px] z-50 text-left"
                style={{ top: "330px", left: "140px" }}
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between border-b border-[#E5E7EB]/40 pb-2 mb-2">
                  <span className="text-xs font-bold text-[#111827]">Petitioner</span>
                  <button onClick={closeAnnotation} className="text-[#6B7280] hover:text-[#111827]">
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
                <p className="text-[11px] text-[#6B7280] font-medium leading-relaxed mb-3">
                  Anjali Khobrekar is the petitioner in this writ petition.
                </p>
                <button className="text-[10px] font-bold text-[#2563EB] hover:text-[#1d4ed8] transition-colors flex items-center gap-0.5">
                  <span>Click to view party details</span>
                </button>
              </div>
            )}

            {/* 3. Ministry of Home Affairs Annotation Popover */}
            {activeAnnotation === "ministry" && (
              <div
                className="absolute bg-white border border-[#E5E7EB] rounded-xl p-4.5 shadow-xl w-[280px] z-50 text-left"
                style={{ top: "420px", left: "330px" }}
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-start gap-3.5">
                  <div className="p-2 rounded-xl bg-blue-50/70 text-[#2563EB] mt-0.5">
                    <Scale className="w-5 h-5" />
                  </div>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-[#111827]">Ministry of Home Affairs</span>
                      <button onClick={closeAnnotation} className="text-[#6B7280] hover:text-[#111827]">
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                    <span className="text-[10px] font-bold text-[#6B7280] uppercase tracking-wider block">
                      Government of India
                    </span>
                    <p className="text-[11px] text-[#6B7280] font-medium leading-relaxed pb-2">
                      Central government ministry responsible for internal security, law and order, police, paramilitary forces, and administration of Union Territories.
                    </p>
                    <button className="text-[11px] font-bold text-[#2563EB] hover:text-[#1d4ed8] flex items-center gap-0.5">
                      <span>View details</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* 4. Article 226 Annotation Popover */}
            {activeAnnotation === "article" && (
              <div
                className="absolute bg-white border border-[#E5E7EB] rounded-xl p-4.5 shadow-xl w-[280px] z-50 text-left"
                style={{ top: "670px", left: "280px" }}
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between border-b border-[#E5E7EB]/40 pb-2 mb-2">
                  <span className="text-xs font-bold text-[#111827]">Article 226</span>
                  <button onClick={closeAnnotation} className="text-[#6B7280] hover:text-[#111827]">
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
                <p className="text-[11px] text-[#6B7280] font-medium leading-relaxed mb-3">
                  Empowers High Courts to issue writs, orders or directions for enforcement of fundamental rights and for any other purpose.
                </p>
                <button className="text-[10px] font-bold text-[#2563EB] hover:text-[#1d4ed8] transition-colors flex items-center gap-0.5">
                  <span>View full text</span>
                  <ExternalLink className="w-3 h-3" />
                </button>
              </div>
            )}

            {/* A4 Sheet Contents */}
            <div className="text-center font-bold tracking-widest text-[15px] space-y-1 mb-8">
              <div>IN THE HIGH COURT OF JUDICATURE AT BOMBAY</div>
              <div>CIVIL APPELLATE JURISDICTION</div>
            </div>

            <div className="text-center font-bold uppercase tracking-wider text-xs mb-10">
              WRIT PETITION (CIVIL) NO.{" "}
              <span
                onClick={(e) => handleAnnotationClick("petition", e)}
                className={`cursor-pointer px-1 py-0.5 rounded border transition-colors select-none font-bold ${
                  activeAnnotation === "petition"
                    ? "bg-blue-100/60 text-[#2563EB] border-[#2563EB]"
                    : "bg-[#EFF6FF] text-[#2563EB] border-[#2563EB]/30 hover:border-[#2563EB]"
                }`}
              >
                2456 OF 2024
              </span>
            </div>

            {/* Parties */}
            <div className="space-y-6 mb-12">
              <div className="flex justify-between items-start gap-4">
                <div className="w-[320px]">
                  <span
                    onClick={(e) => handleAnnotationClick("petitioner", e)}
                    className={`cursor-pointer px-1 py-0.5 rounded border transition-colors font-bold ${
                      activeAnnotation === "petitioner"
                        ? "bg-blue-100/60 text-[#2563EB] border-[#2563EB]"
                        : "bg-[#EFF6FF] text-[#2563EB] border-[#2563EB]/30 hover:border-[#2563EB]"
                    }`}
                  >
                    Anjali Khobrekar
                  </span>
                  <div className="text-xs font-semibold text-[#6B7280] mt-1 italic">
                    Age: 34 years, Occ: Advocate <br />
                    R/o 12, Law Residency, Dadar, Mumbai – 400014.
                  </div>
                </div>
                <div className="font-bold uppercase tracking-widest text-xs self-center">
                  ... Petitioner
                </div>
              </div>

              <div className="text-center font-bold tracking-widest text-xs uppercase my-4">
                VERSUS
              </div>

              <div className="space-y-6">
                <div className="flex justify-between items-start gap-4">
                  <div className="w-[320px]">
                    <span className="font-bold">Union of India</span>
                    <div className="text-xs font-semibold text-[#6B7280] mt-1 leading-relaxed">
                      Through Secretary,{" "}
                      <span
                        onClick={(e) => handleAnnotationClick("ministry", e)}
                        className={`cursor-pointer px-1 py-0.5 rounded border transition-colors font-bold ${
                          activeAnnotation === "ministry"
                            ? "bg-blue-100/60 text-[#2563EB] border-[#2563EB]"
                            : "bg-[#EFF6FF] text-[#2563EB] border-[#2563EB]/30 hover:border-[#2563EB]"
                        }`}
                      >
                        Ministry of Home Affairs
                      </span>
                      , <br />
                      North Block, New Delhi – 110001.
                    </div>
                  </div>
                  <div className="font-bold uppercase tracking-widest text-xs self-center">
                    ... Respondent No. 1
                  </div>
                </div>

                <div className="text-center font-bold tracking-widest text-xs uppercase my-2">
                  AND
                </div>

                <div className="flex justify-between items-start gap-4">
                  <div className="w-[320px]">
                    <span className="font-bold">State of Maharashtra</span>
                    <div className="text-xs font-semibold text-[#6B7280] mt-1">
                      Through Chief Secretary, <br />
                      Mantralaya, Mumbai – 400032.
                    </div>
                  </div>
                  <div className="font-bold uppercase tracking-widest text-xs self-center">
                    ... Respondent No. 2
                  </div>
                </div>
              </div>
            </div>

            {/* Separator line */}
            <div className="w-full h-[1.5px] bg-[#111827]/80 my-8"></div>

            {/* Writ petition label */}
            <div className="text-center font-bold uppercase tracking-wider text-xs mb-8">
              WRIT PETITION UNDER{" "}
              <span
                onClick={(e) => handleAnnotationClick("article", e)}
                className={`cursor-pointer px-1 py-0.5 rounded border transition-colors font-bold ${
                  activeAnnotation === "article"
                    ? "bg-blue-100/60 text-[#2563EB] border-[#2563EB]"
                    : "bg-[#EFF6FF] text-[#2563EB] border-[#2563EB]/30 hover:border-[#2563EB]"
                }`}
              >
                ARTICLE 226
              </span>{" "}
              OF THE CONSTITUTION OF INDIA
            </div>

            {/* Body petition details */}
            <div className="space-y-4 text-xs font-medium text-[#111827] leading-relaxed text-justify mb-24">
              <p>The humble petition of the Petitioner above-named</p>
              <p className="font-bold uppercase tracking-wider text-[11px] mb-2">
                MOST RESPECTFULLY SHOWETH:
              </p>
              <p>
                1. That the Petitioner is an advocate by profession and is presently practicing at the
                Bombay High Court. The Petitioner has been actively engaged in social work and legal advocacy
                for civil liberties and public transparency over the last decade.
              </p>
              <p>
                2. That this petition is filed under Article 226 of the Constitution of India challenging
                the arbitrary actions of the Respondent authorities in denying basic administrative clearances
                without assigning specific reasons or conducting statutory hearings.
              </p>
              <p>
                3. That the failure of the Respondent to execute standard protocols constitutes a direct breach
                of fundamental principles of natural justice and fair play.
              </p>
            </div>

            {/* Floating Search prompt bar (Ask Clausely AI anything Ctrl+Space) */}
            <div className="absolute bottom-8 left-1/2 -translate-x-1/2 w-[540px] bg-[#FFFFFF] border border-[#E5E7EB] focus-within:border-[#2563EB] focus-within:ring-4 focus-within:ring-blue-100 rounded-full py-2.5 px-5 shadow-2xl flex items-center justify-between select-none z-45 transition-all">
              <input
                type="text"
                value={askText}
                onChange={(e) => setAskText(e.target.value)}
                placeholder="Ask Clausely AI anything... (Ctrl + Space)"
                className="flex-1 text-xs text-[#111827] placeholder-[#6B7280] font-semibold bg-transparent outline-none border-none focus:ring-0 mr-3"
              />
              <div className="flex items-center gap-3.5">
                <button className="p-1.5 text-[#6B7280] hover:text-[#111827] rounded-full hover:bg-[#F8F9FA] transition-all">
                  <Mic className="w-4 h-4" />
                </button>
                <button className="p-1.5 text-[#6B7280] hover:text-[#111827] rounded-full hover:bg-[#F8F9FA] transition-all">
                  <AudioLines className="w-4 h-4" />
                </button>
                <button className="bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] text-white p-2 rounded-full hover:scale-105 active:scale-95 shadow-md transition-all">
                  <Sparkles className="w-4.5 h-4.5" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Status Bar at Bottom */}
        <footer className="h-8 bg-white border-t border-[#E5E7EB] px-5 flex items-center justify-between select-none text-[11px] font-semibold text-[#6B7280]">
          <div className="flex items-center gap-4.5">
            <span>Page 1 of 23</span>
            <span>Words: 5,489</span>
            <div className="flex items-center gap-1 cursor-pointer hover:text-[#111827]">
              <span>English (India)</span>
              <ChevronDown className="w-3.5 h-3.5" />
            </div>
          </div>
          <div>
            <span>All changes saved</span>
          </div>
          <div className="flex items-center gap-3">
            <button className="hover:text-[#111827] transition-all">
              <Grid className="w-4 h-4" />
            </button>
            <button className="hover:text-[#111827] transition-all">
              <AlignLeft className="w-4 h-4" />
            </button>
            <div className="flex items-center gap-2">
              <Minus onClick={() => setZoom(Math.max(50, zoom - 10))} className="w-3.5 h-3.5 cursor-pointer hover:text-[#111827]" />
              <span className="w-8 text-center">{zoom}%</span>
              <Plus onClick={() => setZoom(Math.min(200, zoom + 10))} className="w-3.5 h-3.5 cursor-pointer hover:text-[#111827]" />
            </div>
          </div>
        </footer>
      </div>

      {/* Clausely AI Right Sidebar panel */}
      <div className="hidden lg:block">
        <ClauselyAIPanel />
      </div>
    </div>
  );
}
