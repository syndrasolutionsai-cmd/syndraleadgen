import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createCampaign, launchCampaign } from "../api/client";

const STEPS = ["Target", "Message", "Settings", "Launch"];

const INDUSTRIES = ["SaaS", "B2B Software", "Tech", "Fintech", "HR Tech", "MarTech", "E-commerce", "Consulting", "Digital Agency", "Recruitment"];
const ROLES = ["CEO", "Co-Founder", "CRO", "VP Sales", "Head of Sales", "Director Comercial", "Sales Director", "Account Executive"];
const GEOS = ["Spain", "United States", "United Kingdom", "France", "Germany", "Mexico", "Argentina", "Colombia", "Brazil", "Portugal"];
const LANGUAGES = [{ value: "es", label: "Spanish" }, { value: "en", label: "English" }, { value: "fr", label: "French" }, { value: "de", label: "German" }];

function StepIndicator({ current }: { current: number }) {
  return (
    <div className="flex items-center gap-2 mb-8">
      {STEPS.map((label, i) => (
        <div key={label} className="flex items-center gap-2">
          <div className={`flex items-center gap-2`}>
            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold transition-colors ${
              i < current ? "bg-blue-600 text-white" : i === current ? "bg-blue-600 text-white" : "bg-slate-100 text-slate-400"
            }`}>{i < current ? "✓" : i + 1}</div>
            <span className={`text-sm font-medium ${i === current ? "text-blue-600" : i < current ? "text-slate-600" : "text-slate-400"}`}>{label}</span>
          </div>
          {i < STEPS.length - 1 && <div className={`flex-1 h-px w-8 mx-1 ${i < current ? "bg-blue-600" : "bg-slate-200"}`} />}
        </div>
      ))}
    </div>
  );
}

function TagSelect({ options, selected, onChange, placeholder }: {
  options: string[]; selected: string[]; onChange: (v: string[]) => void; placeholder: string;
}) {
  function toggle(opt: string) {
    onChange(selected.includes(opt) ? selected.filter(x => x !== opt) : [...selected, opt]);
  }
  return (
    <div>
      <div className="flex flex-wrap gap-2">
        {options.map(opt => (
          <button key={opt} type="button" onClick={() => toggle(opt)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
              selected.includes(opt) ? "bg-blue-600 text-white border-blue-600" : "bg-white text-slate-600 border-slate-200 hover:border-blue-300"
            }`}>
            {opt}
          </button>
        ))}
      </div>
      {selected.length === 0 && <p className="text-xs text-slate-400 mt-2">{placeholder}</p>}
    </div>
  );
}

export function CampaignWizard() {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Step 1 — Target
  const [name, setName] = useState("");
  const [industries, setIndustries] = useState<string[]>([]);
  const [roles, setRoles] = useState<string[]>([]);
  const [geo, setGeo] = useState("Spain");
  const [sizeMin, setSizeMin] = useState(15);
  const [sizeMax, setSizeMax] = useState(200);

  // Step 2 — Message
  const [niche, setNiche] = useState("");
  const [valueProp, setValueProp] = useState("");
  const [language, setLanguage] = useState("es");

  // Step 3 — Settings
  const [batchSize, setBatchSize] = useState(25);
  const [reviewPct, setReviewPct] = useState(20);
  const [minIcpScore, setMinIcpScore] = useState(65);

  async function handleLaunch() {
    setLoading(true);
    setError("");
    try {
      const campaign = await createCampaign({
        name,
        niche,
        value_prop: valueProp,
        language,
        batch_size: batchSize,
        review_pct: reviewPct,
        icp_config: {
          industries,
          roles,
          geography: [geo],
          company_size: { min: sizeMin, max: sizeMax },
          tech_signals: [],
          exclude_signals: [],
          min_icp_score: minIcpScore,
        },
      });
      await launchCampaign(campaign.id);
      navigate("/dashboard");
    } catch (e: any) {
      setError("Failed to launch campaign. Please try again.");
      setLoading(false);
    }
  }

  const labelClass = "block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2";
  const inputClass = "w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white";

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">New Campaign</h1>
        <p className="text-sm text-slate-400 mt-1">Set up your outbound campaign in 4 steps</p>
      </div>

      <StepIndicator current={step} />

      {/* Step 1: Target */}
      {step === 0 && (
        <div className="space-y-6">
          <div>
            <label className={labelClass}>Campaign name</label>
            <input className={inputClass} value={name} onChange={e => setName(e.target.value)}
              placeholder="e.g. Q2 2026 — SaaS Leaders Spain" />
          </div>
          <div>
            <label className={labelClass}>Industries</label>
            <TagSelect options={INDUSTRIES} selected={industries} onChange={setIndustries} placeholder="Select at least one industry" />
          </div>
          <div>
            <label className={labelClass}>Target roles</label>
            <TagSelect options={ROLES} selected={roles} onChange={setRoles} placeholder="Select target roles" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Geography</label>
              <select className={inputClass} value={geo} onChange={e => setGeo(e.target.value)}>
                {GEOS.map(g => <option key={g}>{g}</option>)}
              </select>
            </div>
            <div>
              <label className={labelClass}>Company size</label>
              <div className="flex items-center gap-2">
                <input type="number" className={inputClass} value={sizeMin} onChange={e => setSizeMin(+e.target.value)} placeholder="Min" />
                <span className="text-slate-400 text-sm">–</span>
                <input type="number" className={inputClass} value={sizeMax} onChange={e => setSizeMax(+e.target.value)} placeholder="Max" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Step 2: Message */}
      {step === 1 && (
        <div className="space-y-6">
          <div>
            <label className={labelClass}>Niche description</label>
            <input className={inputClass} value={niche} onChange={e => setNiche(e.target.value)}
              placeholder="e.g. B2B SaaS companies in Spain scaling outbound sales" />
            <p className="text-xs text-slate-400 mt-1">Used by Claude to frame the message context</p>
          </div>
          <div>
            <label className={labelClass}>Your value proposition</label>
            <textarea
              className={`${inputClass} h-28 resize-none`}
              value={valueProp} onChange={e => setValueProp(e.target.value)}
              placeholder="Describe what you offer and why this prospect should care. Be specific — this becomes the core of every email."
            />
          </div>
          <div>
            <label className={labelClass}>Email language</label>
            <select className={inputClass} value={language} onChange={e => setLanguage(e.target.value)}>
              {LANGUAGES.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
            </select>
          </div>
        </div>
      )}

      {/* Step 3: Settings */}
      {step === 2 && (
        <div className="space-y-6">
          <div>
            <label className={labelClass}>Batch size — {batchSize} prospects</label>
            <input type="range" min={10} max={200} step={5} value={batchSize} onChange={e => setBatchSize(+e.target.value)}
              className="w-full accent-blue-600" />
            <div className="flex justify-between text-xs text-slate-400 mt-1"><span>10</span><span>200</span></div>
          </div>
          <div>
            <label className={labelClass}>Human review — {reviewPct}% of emails</label>
            <input type="range" min={5} max={100} step={5} value={reviewPct} onChange={e => setReviewPct(+e.target.value)}
              className="w-full accent-blue-600" />
            <div className="flex justify-between text-xs text-slate-400 mt-1"><span>5%</span><span>100%</span></div>
            <p className="text-xs text-slate-400 mt-1">Plus all mandatory reviews (low verification score, first campaign)</p>
          </div>
          <div>
            <label className={labelClass}>Minimum ICP score — {minIcpScore}</label>
            <input type="range" min={50} max={90} step={5} value={minIcpScore} onChange={e => setMinIcpScore(+e.target.value)}
              className="w-full accent-blue-600" />
            <div className="flex justify-between text-xs text-slate-400 mt-1"><span>50 (broader)</span><span>90 (strict)</span></div>
          </div>
        </div>
      )}

      {/* Step 4: Launch */}
      {step === 3 && (
        <div className="space-y-4">
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3">
            <h3 className="text-sm font-semibold text-slate-700">Campaign Summary</h3>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div><span className="text-slate-400">Name:</span> <span className="font-medium text-slate-800">{name}</span></div>
              <div><span className="text-slate-400">Geography:</span> <span className="font-medium text-slate-800">{geo}</span></div>
              <div><span className="text-slate-400">Industries:</span> <span className="font-medium text-slate-800">{industries.join(", ") || "—"}</span></div>
              <div><span className="text-slate-400">Roles:</span> <span className="font-medium text-slate-800">{roles.join(", ") || "—"}</span></div>
              <div><span className="text-slate-400">Company size:</span> <span className="font-medium text-slate-800">{sizeMin}–{sizeMax}</span></div>
              <div><span className="text-slate-400">Language:</span> <span className="font-medium text-slate-800">{LANGUAGES.find(l => l.value === language)?.label}</span></div>
              <div><span className="text-slate-400">Batch size:</span> <span className="font-medium text-slate-800">{batchSize} prospects</span></div>
              <div><span className="text-slate-400">Review %:</span> <span className="font-medium text-slate-800">{reviewPct}%</span></div>
              <div className="col-span-2"><span className="text-slate-400">Value prop:</span> <span className="font-medium text-slate-800">{valueProp || "—"}</span></div>
            </div>
          </div>
          {error && <p className="text-red-600 text-sm">{error}</p>}
        </div>
      )}

      {/* Nav buttons */}
      <div className="flex justify-between mt-8">
        <button onClick={() => step > 0 ? setStep(step - 1) : navigate("/dashboard")}
          className="px-4 py-2 text-sm text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50">
          {step === 0 ? "Cancel" : "← Back"}
        </button>
        {step < 3 ? (
          <button onClick={() => setStep(step + 1)}
            disabled={step === 0 && (!name || industries.length === 0 || roles.length === 0)}
            className="px-5 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed">
            Next →
          </button>
        ) : (
          <button onClick={handleLaunch} disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2">
            {loading ? "Launching..." : "🚀 Launch Campaign"}
          </button>
        )}
      </div>
    </div>
  );
}
