import Chatbot from "./components/Chatbot";
import React, { useEffect, useState } from "react";
import { Routes, Route, Link, useNavigate, useParams } from "react-router-dom";
import API from "./services/api";
import {
  ShieldCheck, FileText, Search, CheckCircle2, AlertTriangle,
  XCircle, Upload, Calculator, MapPin, ClipboardCheck, ArrowRight,
  LogOut, UserRound, LayoutDashboard, Languages, Mic
} from "lucide-react";

const demoUser = () => JSON.parse(localStorage.getItem("user") || "null");

function Protected({ children }) {
  return localStorage.getItem("token") ? children : <Login />;
}

function Layout({ children }) {
  const nav = useNavigate();

  const logout = () => {
    localStorage.clear();
    nav("/login");
  };

  return (
    <div className="app-shell">

      <aside className="sidebar">

        <div className="brand">
          <ShieldCheck size={28}/>
          <span>SchemeSahay</span>
        </div>

        <nav>
          <Link to="/dashboard">
            <LayoutDashboard/>
            Dashboard
          </Link>

          <Link to="/profile">
            <UserRound/>
            My Profile
          </Link>

          <Link to="/documents">
            <FileText/>
            Documents
          </Link>

          <Link to="/schemes">
            <Search/>
            Schemes
          </Link>

          <Link to="/simulator">
            <Calculator/>
            Simulator
          </Link>

          <Link to="/partners">
            <MapPin/>
            Partners
          </Link>

          <Link to="/applications">
            <ClipboardCheck/>
            Applications
          </Link>
        </nav>

        <button className="logout" onClick={logout}>
          <LogOut/>
          Logout
        </button>

      </aside>

      <main className="main">
        {children}
      </main>

      <Chatbot />

    </div>
  );
}

function Landing() {
  const nav = useNavigate();
  return <div className="landing">
    <div className="hero">
      <div className="eyebrow">AI-DRIVEN SCHEME MATCHING</div>
      <h1>From Scheme Discovery<br/><span>to Application Readiness.</span></h1>
      <p>Discover relevant government schemes, understand the evidence behind eligibility, fix avoidable application issues, simulate finances, route to an appropriate channel partner and track your application.</p>
      <div className="hero-actions">
        <button className="primary" onClick={() => nav("/register")}>Get Started <ArrowRight/></button>
        <button className="secondary" onClick={() => nav("/login")}>Sign In</button>
      </div>
    </div>
    <div className="feature-grid">
      {[
        ["AI Scheme Matching","Natural-language understanding plus structured scheme rules."],
        ["Evidence-Based Eligibility","See the requirement, your value, evidence and status."],
        ["Application Readiness","Find missing documents and inconsistencies before submission."],
        ["Financial What-If","Explore project cost, loan and repayment scenarios."],
        ["Partner Routing","Prioritize suitable authorized channels, not just the nearest branch."],
        ["Application Tracking","Follow the application journey and required actions."]
      ].map(([a,b]) => <div className="feature" key={a}><CheckCircle2/><h3>{a}</h3><p>{b}</p></div>)}
    </div>
  </div>
}

function Login() {
  const nav = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const r = await API.post("/auth/login", {
        email,
        password
      });

      localStorage.setItem("token", r.data.access_token);
      localStorage.setItem("user", JSON.stringify(r.data.user));

      nav("/dashboard");
    } catch (err) {
      setError(
        err.response?.data?.detail || "Login failed"
      );
    }
  };

  return (
    <Auth
      title="Welcome back"
      subtitle="Continue your SchemeSahay journey"
    >
      <form onSubmit={submit}>

        <Field
          label="Email"
          value={email}
          set={(e) => setEmail(e.target.value)}
          type="email"
        />

        <Field
          label="Password"
          value={password}
          set={(e) => setPassword(e.target.value)}
          type="password"
        />

        {error && <div className="error">{error}</div>}

        <button className="primary full">
          Sign In
        </button>

        <p className="center">
          New here? <Link to="/register">Create account</Link>
        </p>

      </form>
    </Auth>
  );
}

function Register() {
  const nav=useNavigate(); const [form,setForm]=useState({name:"",email:"",password:"",phone:""});const [error,setError]=useState("");
  const set=k=>e=>setForm({...form,[k]:e.target.value});
  const submit=async e=>{e.preventDefault();setError("");try{await API.post("/auth/register",form);nav("/login")}catch(err){setError(err.response?.data?.detail||"Registration failed")}};
  return <Auth title="Create your profile" subtitle="Start your scheme discovery journey"><form onSubmit={submit}>
    <Field label="Full name" value={form.name} set={set("name")}/><Field label="Email" value={form.email} set={set("email")} type="email"/><Field label="Phone" value={form.phone} set={set("phone")}/><Field label="Password" value={form.password} set={set("password")} type="password"/>
    {error&&<div className="error">{error}</div>}<button className="primary full">Create Account</button><p className="center">Already registered? <Link to="/login">Sign in</Link></p>
  </form></Auth>
}

function Auth({title,subtitle,children}){return <div className="auth-page"><div className="auth-card"><div className="brand dark"><ShieldCheck/> SchemeSahay</div><h1>{title}</h1><p>{subtitle}</p>{children}</div></div>}
function Field({label,value,set,type="text"}){return <label className="field"><span>{label}</span><input value={value??""} onChange={set} type={type}/></label>}

function Dashboard(){
  const [profile,setProfile]=useState({}); const [apps,setApps]=useState([]); const nav=useNavigate();
  useEffect(()=>{Promise.all([API.get("/profile"),API.get("/applications")]).then(([p,a])=>{setProfile(p.data);setApps(a.data)})},[]);
  const completeness=["age","state","district","category","income","occupation","education"].filter(k=>profile[k]!==null&&profile[k]!==undefined&&profile[k]!=="" ).length;
  return <Layout><Top title="Dashboard" subtitle={`Welcome, ${demoUser()?.name||"Entrepreneur"}`}/>
    <div className="grid-4">
      <Stat label="Profile Completion" value={`${Math.round(completeness/7*100)}%`} icon={<UserRound/>}/>
      <Stat label="Documents" value="Manage" icon={<FileText/>} onClick={()=>nav("/documents")}/>
      <Stat label="Schemes" value="Explore" icon={<Search/>} onClick={()=>nav("/schemes")}/>
      <Stat label="Applications" value={apps.length} icon={<ClipboardCheck/>}/>
    </div>
    <div className="grid-2">
      <div className="card"><h2>Core Journey</h2><div className="journey">{["Discover","Match","Explain","Verify","Prevent Errors","Simulate","Route","Apply","Track"].map((x,i)=><div className="journey-step" key={x}><span>{i+1}</span>{x}</div>)}</div></div>
      <div className="card highlight"><h2>Application Readiness ⭐</h2><p>Before submission, SchemeSahay checks eligibility evidence, required documents, profile completeness and financial consistency.</p><button className="primary" onClick={()=>nav("/schemes")}>Find a Scheme <ArrowRight/></button></div>
    </div>
    <div className="card"><h2>Your applications</h2>{apps.length===0?<Empty text="No applications yet. Start by exploring schemes."/>:apps.map(a=><div className="list-row" key={a.id}><div><b>Application</b><small>Status: {a.status}</small></div><span className="pill">{a.status}</span></div>)}</div>
  </Layout>
}

function Top({title,subtitle}){return <header className="top"><div><h1>{title}</h1><p>{subtitle}</p></div><div className="top-actions"><button className="icon-btn"><Languages/> EN</button><button className="icon-btn"><Mic/></button></div></header>}
function Stat({label,value,icon,onClick}){return <div className={`stat ${onClick?"clickable":""}`} onClick={onClick}><div className="stat-icon">{icon}</div><div><span>{label}</span><strong>{value}</strong></div></div>}
function Empty({text}){return <div className="empty">{text}</div>}

function Profile() {
  const [form, setForm] = useState({});
  const [msg, setMsg] = useState("");

  useEffect(() => {
    API.get("/profile").then((r) => {
      setForm(r.data);
    });
  }, []);

  const set = (k) => (e) => {
    const numericFields = [
      "age",
      "income",
      "family_size",
      "dependents",
      "land_ownership",
      "project_cost",
      "required_loan"
    ];

    setForm({
      ...form,
      [k]: numericFields.includes(k)
        ? e.target.value === ""
          ? null
          : Number(e.target.value)
        : e.target.value
    });
  };

  const save = async (e) => {
    e.preventDefault();

    try {
      await API.put("/profile", form);
      setMsg("Profile saved successfully.");
    } catch (err) {
      setMsg("Failed to save profile.");
    }
  };

  return (
    <Layout>
      <Top
        title="My Profile"
        subtitle="Build the evidence-backed profile used for scheme matching"
      />

      <form className="card form-grid" onSubmit={save}>
        <h2 className="span">Personal Information</h2>

        {[
          "age",
          "state",
          "district",
          "category",
          "income",
          "occupation",
          "education",
          "employment_status",
          "business_type",
          "business_status",
          "project_cost",
          "required_loan"
        ].map((k) => (
          <Field
            key={k}
            label={k
              .replaceAll("_", " ")
              .replace(/\b\w/g, (c) => c.toUpperCase())}
            value={form[k] ?? ""}
            set={set(k)}
            type={
              ["age", "income", "project_cost", "required_loan"].includes(k)
                ? "number"
                : "text"
            }
          />
        ))}

        <div className="check span">
          <label>
            <input
              type="checkbox"
              checked={!!form.bank_account}
              onChange={(e) =>
                setForm({
                  ...form,
                  bank_account: e.target.checked
                })
              }
            />
            Bank account available
          </label>

          <label>
            <input
              type="checkbox"
              checked={!!form.aadhaar_available}
              onChange={(e) =>
                setForm({
                  ...form,
                  aadhaar_available: e.target.checked
                })
              }
            />
            Aadhaar available
          </label>

          <label>
            <input
              type="checkbox"
              checked={!!form.disability_status}
              onChange={(e) =>
                setForm({
                  ...form,
                  disability_status: e.target.checked
                })
              }
            />
            Disability status
          </label>
        </div>

        <div className="span">
          <button className="primary" type="submit">
            Save Profile
          </button>

          {msg && <span className="success-text">{msg}</span>}
        </div>
      </form>
    </Layout>
  );
}


function Documents() {
  const [docs, setDocs] = useState([]);
  const [type, setType] = useState("aadhaar");
  const [busy, setBusy] = useState(false);

  const load = () => {
    API.get("/documents").then((r) => {
      setDocs(r.data);
    });
  };

  useEffect(() => {
    load();
  }, []);

  const upload = async (e) => {
    const file = e.target.files[0];

    if (!file) return;

    setBusy(true);

    const fd = new FormData();
    fd.append("file", file);

    try {
      await API.post(
        `/documents/upload?document_type=${encodeURIComponent(type)}`,
        fd,
        {
          headers: {
            "Content-Type": "multipart/form-data"
          }
        }
      );

      load();
    } catch (err) {
      console.error(err);
    } finally {
      setBusy(false);
    }
  };

  return (
    <Layout>
      <Top
        title="Documents"
        subtitle="Upload documents and review OCR extraction"
      />

      <div className="card">
        <h2>Upload document</h2>

        <div className="upload-controls">
          <select
            value={type}
            onChange={(e) => setType(e.target.value)}
          >
            <option value="aadhaar">Identity / Aadhaar</option>
            <option value="caste_certificate">Caste Certificate</option>
            <option value="income_certificate">Income Certificate</option>
            <option value="address_proof">Address Proof</option>
            <option value="project_document">
              Project / Course Document
            </option>
            <option value="bank_passbook">Bank Passbook</option>
          </select>

          <label className="upload-btn">
            <Upload />
            {busy ? "Processing..." : "Choose file"}

            <input
              hidden
              type="file"
              accept=".pdf,.png,.jpg,.jpeg,.webp"
              onChange={upload}
            />
          </label>
        </div>

        <p className="muted">
          OCR output is extraction assistance. It is not treated as
          government verification.
        </p>
      </div>

      <div className="card">
        <h2>My documents</h2>

        {docs.length === 0 ? (
          <Empty text="No documents uploaded yet." />
        ) : (
          docs.map((d) => (
            <div className="doc" key={d.id}>
              <div>
                <b>{d.document_name}</b>
                <small>{d.document_type}</small>
              </div>

              <span
                className={`pill ${
                  d.ocr_status === "completed" ? "green" : ""
                }`}
              >
                OCR: {d.ocr_status}
              </span>
            </div>
          ))
        )}
      </div>
    </Layout>
  );
}


function Schemes() {
  const [schemes, setSchemes] = useState([]);
  const [q, setQ] = useState("");
  const [request, setRequest] = useState("");
  const [matches, setMatches] = useState([]);

  const load = () => {
    API.get("/schemes").then((r) => {
      setSchemes(r.data);
    });
  };

  useEffect(() => {
    load();
  }, []);

  const search = () => {
    API.get("/schemes", {
      params: { q }
    }).then((r) => {
      setSchemes(r.data);
    });
  };

  const ai = async () => {
    if (!request) return;

    try {
      const r = await API.post("/matching", {
        request
      });

      setMatches(r.data.results);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <Layout>
      <Top
        title="Scheme Discovery"
        subtitle="Find potentially relevant schemes, then verify eligibility"
      />

      <div className="card">
        <h2>Describe what you need</h2>

        <div className="searchbar">
          <input
            placeholder="Example: I want to start a tailoring business and need ₹2 lakh"
            value={request}
            onChange={(e) => setRequest(e.target.value)}
          />

          <button className="primary" onClick={ai}>
            AI Match <Search />
          </button>
        </div>

        <p className="muted">
          AI matching finds relevant records; the rule engine determines
          the evidence-based eligibility result.
        </p>
      </div>

      {matches.length > 0 && (
        <div className="card">
          <h2>AI Matches</h2>

          <div className="scheme-grid">
            {matches.map((s) => (
              <SchemeCard s={s} key={s.id} />
            ))}
          </div>
        </div>
      )}

      <div className="card">
        <div className="row-between">
          <h2>All schemes</h2>

          <div className="searchbar small">
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search"
            />

            <button onClick={search}>Search</button>
          </div>
        </div>

        <div className="scheme-grid">
          {schemes.map((s) => (
            <SchemeCard s={s} key={s.id} />
          ))}
        </div>
      </div>
    </Layout>
  );
}


function SchemeCard({ s }) {
  const nav = useNavigate();

  return (
    <div className="scheme-card">
      <div className="scheme-tag">{s.category}</div>

      <h3>{s.name}</h3>

      <p>{s.description}</p>

      <div className="scheme-meta">
        <span>Benefit</span>
        <b>{s.benefit_amount}</b>
      </div>

      <button
        className="secondary full"
        onClick={() => nav(`/schemes/${s.id}`)}
      >
        View Eligibility <ArrowRight />
      </button>
    </div>
  );
}


function SchemeDetails() {
  const { id } = useParams();

  const [s, setS] = useState(null);
  const [elig, setElig] = useState(null);
  const [ready, setReady] = useState(null);

  const nav = useNavigate();

  useEffect(() => {
    API.get(`/schemes/${id}`).then((r) => {
      setS(r.data);
    });
  }, [id]);

  const check = async () => {
    const r = await API.post(`/eligibility/check/${id}`);
    setElig(r.data);
  };

  const readiness = async () => {
    const r = await API.post(`/readiness/check/${id}`);
    setReady(r.data);
  };

  const create = async () => {
    const r = await API.post("/applications", {
      scheme_id: id,
      channel: ""
    });

    nav(`/applications/${r.data.id}`);
  };

  if (!s) {
    return (
      <Layout>
        <Empty text="Loading..." />
      </Layout>
    );
  }

  return (
    <Layout>
      <Top
        title={s.name}
        subtitle={s.ministry || "Scheme details"}
      />

      <div className="grid-2">
        <div className="card">
          <h2>About</h2>

          <p>{s.description}</p>

          <div className="facts">
            <b>Benefit</b>
            <span>{s.benefit_amount}</span>

            <b>Category</b>
            <span>{s.category}</span>

            <b>Channel</b>
            <span>{s.application_channel}</span>

            <b>Last verified</b>
            <span>{s.last_verified}</span>
          </div>
        </div>

        <div className="card highlight">
          <h2>Check before applying</h2>

          <p>
            Run the deterministic eligibility and application-readiness
            checks.
          </p>

          <div className="btn-row">
            <button className="primary" onClick={check}>
              Check Eligibility
            </button>

            <button className="secondary" onClick={readiness}>
              Readiness Check
            </button>
          </div>

          {ready && (
            <div className="score">
              <strong>{ready.score}%</strong>
              <span>{ready.label}</span>
            </div>
          )}
        </div>
      </div>

      {elig && (
        <div className="card">
          <h2>Eligibility Evidence</h2>
          <Evidence items={elig.evidence} />
        </div>
      )}

      {ready && (
        <div className="card">
          <h2>Application Readiness ⭐</h2>

          <div className="readiness-grid">
            <div className="big-score">
              {ready.score}%
              <small>{ready.label}</small>
            </div>

            <div>
              <h3>Corrective action plan</h3>

              {ready.actions.length ? (
                ready.actions.map((x, i) => (
                  <div className="action" key={i}>
                    <AlertTriangle />
                    {x}
                  </div>
                ))
              ) : (
                <div className="action good">
                  <CheckCircle2 />
                  No avoidable issues detected
                </div>
              )}
            </div>
          </div>

          <h3>Documents</h3>

          {ready.documents.map((d) => (
            <div className="list-row" key={d.document_type}>
              <span>{d.document}</span>

              <span
                className={`status ${
                  d.status === "SATISFIED" ? "ok" : "bad"
                }`}
              >
                {d.status}
              </span>
            </div>
          ))}
        </div>
      )}

      <div className="card">
        <h2>Next step</h2>

        <button className="primary" onClick={create}>
          Create Application <ArrowRight />
        </button>
      </div>
    </Layout>
  );
}


function Evidence({ items }) {
  return (
    <div className="evidence">
      {items.map((x, i) => (
        <div className="evidence-row" key={i}>
          <div className="evidence-icon">
            {x.status === "SATISFIED" ? (
              <CheckCircle2 />
            ) : x.status === "NOT_SATISFIED" ? (
              <XCircle />
            ) : (
              <AlertTriangle />
            )}
          </div>

          <div>
            <b>{x.requirement}</b>

            <small>
              Required: {x.required_value} · Your value:{" "}
              {x.user_value ?? "Missing"}
            </small>

            <small>
              Evidence/source: {x.source}
            </small>
          </div>

          <span
            className={`status ${
              x.status === "SATISFIED"
                ? "ok"
                : x.status === "NOT_SATISFIED"
                ? "bad"
                : "warn"
            }`}
          >
            {x.status.replaceAll("_", " ")}
          </span>
        </div>
      ))}
    </div>
  );
}


function Simulator() {
  const [f, setF] = useState({
    principal: 600000,
    annual_rate: 8,
    tenure_months: 60,
    own_contribution: 200000,
    moratorium_months: 0
  });

  const [r, setR] = useState(null);

  const calc = async () => {
    const result = await API.post("/simulator/calculate", f);
    setR(result.data);
  };

  const set = (k) => (e) => {
    setF({
      ...f,
      [k]: Number(e.target.value)
    });
  };

  return (
    <Layout>
      <Top
        title="Financial What-If Simulator"
        subtitle="Explore scenarios using explicit assumptions"
      />

      <div className="grid-2">
        <div className="card form-grid">
          <Field
            label="Loan amount"
            value={f.principal}
            set={set("principal")}
            type="number"
          />

          <Field
            label="Annual interest rate %"
            value={f.annual_rate}
            set={set("annual_rate")}
            type="number"
          />

          <Field
            label="Tenure (months)"
            value={f.tenure_months}
            set={set("tenure_months")}
            type="number"
          />

          <Field
            label="Own contribution"
            value={f.own_contribution}
            set={set("own_contribution")}
            type="number"
          />

          <Field
            label="Moratorium (months)"
            value={f.moratorium_months}
            set={set("moratorium_months")}
            type="number"
          />

          <button className="primary span" onClick={calc}>
            Calculate
          </button>
        </div>

        <div className="card">
          {r ? (
            <>
              <h2>Estimated result</h2>

              <div className="result-grid">
                <Stat
                  label="Estimated EMI"
                  value={`₹${r.estimated_emi.toLocaleString()}`}
                  icon={<Calculator />}
                />

                <Stat
                  label="Interest"
                  value={`₹${r.estimated_interest.toLocaleString()}`}
                  icon={<Calculator />}
                />

                <Stat
                  label="Total repayment"
                  value={`₹${r.estimated_total_repayment.toLocaleString()}`}
                  icon={<Calculator />}
                />
              </div>

              <p className="muted">{r.note}</p>
            </>
          ) : (
            <Empty text="Enter a scenario and calculate." />
          )}
        </div>
      </div>
    </Layout>
  );
}


function Partners() {
  const [data, setData] = useState(null);

  useEffect(() => {
    API.get("/partners").then((r) => {
      setData(r.data);
    });
  }, []);

  return (
    <Layout>
      <Top
        title="Channel Partners"
        subtitle="Route to suitable assistance channels rather than simply the nearest location"
      />

      <div className="card">
        <h2>Available demo partners</h2>

        {data?.map((p) => (
          <div className="partner" key={p.id}>
            <div>
              <h3>{p.name}</h3>
              <small>
                {p.type} · {p.district}
              </small>

              <p>{p.services?.join(" · ")}</p>
            </div>

            <div className="distance">
              {p.distance_km} km
            </div>
          </div>
        ))}
      </div>
    </Layout>
  );
}


function Applications() {
  const [apps, setApps] = useState([]);

  useEffect(() => {
    API.get("/applications").then((r) => {
      setApps(r.data);
    });
  }, []);

  return (
    <Layout>
      <Top
        title="Applications"
        subtitle="Track your application journey"
      />

      <div className="card">
        {apps.length ? (
          apps.map((a) => (
            <div className="list-row" key={a.id}>
              <div>
                <b>Application {a.id.slice(-6)}</b>
                <small>Status: {a.status}</small>
              </div>

              <Link
                className="secondary-link"
                to={`/applications/${a.id}`}
              >
                Open
              </Link>
            </div>
          ))
        ) : (
          <Empty text="No applications yet." />
        )}
      </div>
    </Layout>
  );
}


function ApplicationDetail() {
  const { id } = useParams();

  const [a, setA] = useState(null);
  const [busy, setBusy] = useState(false);

  const load = () => {
    API.get(`/applications/${id}`).then((r) => {
      setA(r.data);
    });
  };

  useEffect(() => {
    load();
  }, [id]);

  const submit = async () => {
    setBusy(true);

    try {
      await API.post(`/applications/${id}/submit`);
      load();
    } finally {
      setBusy(false);
    }
  };

  if (!a) {
    return (
      <Layout>
        <Empty text="Loading..." />
      </Layout>
    );
  }

  return (
    <Layout>
      <Top
        title="Application"
        subtitle="Your guided application and tracking timeline"
      />

      <div className="card">
        <h2>
          Status: <span className="pill">{a.status}</span>
        </h2>

        <button
          className="primary"
          disabled={busy || a.status === "submitted"}
          onClick={submit}
        >
          {busy ? "Submitting..." : "Submit Demo Application"}
        </button>

        <p className="muted">
          Submission here demonstrates the workflow. Real institutional
          submission requires an authorized integration or official portal.
        </p>
      </div>

      <div className="card">
        <h2>Timeline</h2>

        {a.events?.map((e) => (
          <div className="timeline" key={e.id}>
            <div className="dot" />

            <div>
              <b>{e.status}</b>
              <p>{e.description}</p>

              {e.action_required && (
                <small>
                  Action: {e.action_required}
                </small>
              )}
            </div>
          </div>
        ))}
      </div>
    </Layout>
  );
}
export default function App(){
 return <Routes>
  <Route path="/" element={<Landing/>}/><Route path="/login" element={<Login/>}/><Route path="/register" element={<Register/>}/>
  <Route path="/dashboard" element={<Protected><Dashboard/></Protected>}/><Route path="/profile" element={<Protected><Profile/></Protected>}/><Route path="/documents" element={<Protected><Documents/></Protected>}/>
  <Route path="/schemes" element={<Protected><Schemes/></Protected>}/><Route path="/schemes/:id" element={<Protected><SchemeDetails/></Protected>}/>
  <Route path="/simulator" element={<Protected><Simulator/></Protected>}/><Route path="/partners" element={<Protected><Partners/></Protected>}/>
  <Route path="/applications" element={<Protected><Applications/></Protected>}/><Route path="/applications/:id" element={<Protected><ApplicationDetail/></Protected>}/>
 </Routes>
}
