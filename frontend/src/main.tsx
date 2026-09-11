import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { api } from './services/api';
import type { ApiDocument, CallJob, Company, ConfigStatus } from './types';
import './styles.css';

type SavedCompany = { id: number; name: string; phone_number: string };
const RECENT_KEY = 'denwa_recent_companies';

function readRecent(): SavedCompany[] {
  try {
    const raw = localStorage.getItem(RECENT_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed)
      ? parsed.filter((p): p is SavedCompany => !!p && typeof p.id === 'number' && typeof p.name === 'string')
      : [];
  } catch { return []; }
}

function writeRecent(list: SavedCompany[]) {
  try { localStorage.setItem(RECENT_KEY, JSON.stringify(list.slice(0, 5))); } catch { /* ignore */ }
}

type IconName =
  | 'grid' | 'phone' | 'history' | 'book' | 'numbers' | 'follow' | 'chart' | 'settings'
  | 'team' | 'search' | 'calendar' | 'chevron' | 'arrowUp' | 'arrowDown' | 'play'
  | 'download' | 'back' | 'more' | 'check' | 'clock' | 'cloud' | 'brain' | 'message'
  | 'database' | 'menu' | 'close' | 'upload' | 'refresh' | 'external';

function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  const common = { width: size, height: size, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 1.8, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const };
  const paths: Record<IconName, React.ReactNode> = {
    grid: <><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></>,
    phone: <><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.4 19.4 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 2 .7 2.9a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.9.3 1.9.6 2.9.7A2 2 0 0 1 22 16.9Z"/></>,
    history: <><path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/><path d="M12 7v5l3 2"/></>,
    book: <><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z"/><path d="M8 6h8M8 10h8"/></>,
    numbers: <><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 7h8M8 11h8M8 15h3M15 15h1"/></>,
    follow: <><path d="M20 7H4"/><path d="m8 3-4 4 4 4"/><path d="M4 17h16"/><path d="m16 13 4 4-4 4"/></>,
    chart: <><path d="M4 19V5"/><path d="M4 19h17"/><path d="m7 15 4-5 3 2 5-7"/></>,
    settings: <><path d="M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-1.8 1.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.5v.2h-2.6v-.2a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.9.3l-.1.1-1.8-1.8.1-.1A1.7 1.7 0 0 0 8 15a1.7 1.7 0 0 0-1.5-1H6.3v-2.6h.2A1.7 1.7 0 0 0 8 10a1.7 1.7 0 0 0-.3-1.9l-.1-.1 1.8-1.8.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.5v-.2h2.6v.2a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.3l.1-.1 1.8 1.8-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.5 1h.2V14h-.2a1.7 1.7 0 0 0-1.5 1Z"/></>,
    team: <><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/></>,
    search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
    calendar: <><rect x="3" y="4" width="18" height="17" rx="2"/><path d="M16 2v4M8 2v4M3 9h18"/></>,
    chevron: <path d="m6 9 6 6 6-6"/>,
    arrowUp: <><path d="M12 19V5"/><path d="m6 11 6-6 6 6"/></>,
    arrowDown: <><path d="M12 5v14"/><path d="m18 13-6 6-6-6"/></>,
    play: <path d="m8 5 11 7-11 7V5Z" fill="currentColor" stroke="none"/>,
    download: <><path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/></>,
    back: <><path d="m15 18-6-6 6-6"/><path d="M9 12h12"/></>,
    more: <><circle cx="5" cy="12" r="1" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="1" fill="currentColor" stroke="none"/><circle cx="19" cy="12" r="1" fill="currentColor" stroke="none"/></>,
    check: <><circle cx="12" cy="12" r="9"/><path d="m8 12 2.5 2.5L16 9"/></>,
    clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
    cloud: <><path d="M17.5 19H8a6 6 0 1 1 5.7-7.8A4.5 4.5 0 0 1 17.5 19Z"/><path d="M12 12v6M9.5 14.5 12 12l2.5 2.5"/></>,
    brain: <><path d="M9.5 4.5a3 3 0 0 0-5.4 2.2A3.5 3.5 0 0 0 5 13.5 3 3 0 0 0 8 19h2V6.5a2 2 0 0 0-.5-2Z"/><path d="M14.5 4.5a3 3 0 0 1 5.4 2.2A3.5 3.5 0 0 1 19 13.5 3 3 0 0 1 16 19h-2V6.5a2 2 0 0 1 .5-2Z"/><path d="M8 9h2M14 9h2M8 14h2M14 14h2"/></>,
    message: <><path d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9.4 9.4 0 0 1-4-.9L3 21l1.9-4.4A8.2 8.2 0 0 1 3 11.5 8.5 8.5 0 0 1 12 3a8.5 8.5 0 0 1 9 8.5Z"/></>,
    database: <><ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v7c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 12v7c0 1.7 3.6 3 8 3s8-1.3 8-3v-7"/></>,
    menu: <><path d="M4 7h16M4 12h16M4 17h16"/></>,
    close: <><path d="m6 6 12 12M18 6 6 18"/></>,
    upload: <><path d="M12 16V4"/><path d="m7 9 5-5 5 5"/><path d="M5 20h14"/></>,
    refresh: <><path d="M20 11a8 8 0 0 0-14.9-3L3 11"/><path d="M3 5v6h6"/><path d="M4 13a8 8 0 0 0 14.9 3L21 13"/><path d="M21 19v-6h-6"/></>,
    external: <><path d="M14 4h6v6"/><path d="m20 4-9 9"/><path d="M18 13v5a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h5"/></>
  };
  return <svg {...common}>{paths[name]}</svg>;
}

const navItems: { label: string; icon: IconName }[] = [
  { label: 'Dashboard', icon: 'grid' },
  { label: 'Missed Calls', icon: 'phone' },
  { label: 'Call History', icon: 'history' },
  { label: 'Knowledge Base', icon: 'book' },
  { label: 'Phone Numbers', icon: 'numbers' },
  { label: 'Follow-up Cases', icon: 'follow' },
  { label: 'Analytics', icon: 'chart' },
  { label: 'Settings', icon: 'settings' },
  { label: 'Team', icon: 'team' },
];

const STORAGE_KEY = 'denwa_company_id';

const statusLabel: Record<string, string> = {
  pending: 'Queued',
  in_progress: 'In Progress',
  completed: 'Completed',
  failed: 'Failed',
};

const followUpLabel = (c: CallJob) => {
  if (c.result?.needs_human_followup) return 'Requires Follow-up';
  if (c.result?.resolved) return 'Answered';
  return statusLabel[c.status] ?? c.status;
};

function toLocalDate(iso: string | null): string {
  if (!iso) return '—';
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function Logo() {
  return <div className="logoMark"><span>⌁</span><b>Denwa</b></div>;
}

function Status({ children }: { children: string }) {
  const key = children.toLowerCase();
  return <span className={`status status-${key.replaceAll(' ', '-').replaceAll('—', '')}`}>{children}</span>;
}

function Sidebar({ active, setActive, open, onClose, company }: { active: string; setActive: (v: string) => void; open: boolean; onClose: () => void; company: Company | null }) {
  return <>
    {open && <div className="mobileOverlay" onClick={onClose} />}
    <aside className={`sidebar ${open ? 'open' : ''}`}>
      <div className="brand"><Logo /><button className="mobileClose" onClick={onClose}><Icon name="close" size={20}/></button></div>
      <div className="agentLabel">AI Callback Support Agent</div>
      <nav>
        {navItems.map(item => <button key={item.label} className={`navItem ${active === item.label ? 'active' : ''}`} onClick={() => { setActive(item.label); onClose(); }}><Icon name={item.icon}/><span>{item.label}</span></button>)}
      </nav>
      <div className="accountCard">
        <div className="avatar">{(company?.name ?? 'A').charAt(0).toUpperCase()}</div>
        <div><strong>{company?.name ?? 'Not set up'}</strong><small>Owner</small></div>
        <Icon name="chevron" size={16}/>
      </div>
    </aside>
  </>;
}

function Header({ onMenu, active, onLogout }: { onMenu: () => void; active: string; onLogout: () => void }) {
  return <header className="topbar">
    <button className="menuBtn" onClick={onMenu}><Icon name="menu" size={21}/></button>
    <div><div className="crumb">Denwa <span>/</span> {active}</div><h1>{active}</h1></div>
    <div className="headerRight">
      <button className="logoutBtn" onClick={onLogout} title="Switch business"><Icon name="numbers" size={15}/> Switch</button>
      <div className="userDot">A</div>
    </div>
  </header>;
}

function LoadingState() {
  return <div className="loadingState"><span className="spinner" /><p>Loading your Denwa workspace…</p></div>;
}

function ErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return <div className="page"><section className="emptyState panel"><div className="emptyIcon"><Icon name="cloud" size={28}/></div><h3>Couldn't reach the backend</h3><p>{message}</p><button className="outlineBtn" onClick={onRetry}>Retry <Icon name="refresh" size={15}/></button></section></div>;
}

function Onboarding({ onCreate, busy, error, onFindByPhone, findBusy, recent, onSignIn }: { onCreate: (name: string, phone: string) => void; busy: boolean; error: string | null; onFindByPhone: (phone: string) => void; findBusy: boolean; recent: SavedCompany[]; onSignIn: (id: number) => void }) {
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [findOpen, setFindOpen] = useState(false);
  const [findPhone, setFindPhone] = useState('');
  return <div className="onboarding">
    <div className="onboardingCard">
      <Logo />
      <h2>Connect your business</h2>
      <p>Register your business number so Denwa can turn missed calls into AI callbacks.</p>
      <form onSubmit={(e) => { e.preventDefault(); onCreate(name, phone); }}>
        <label>Business name<input value={name} placeholder="e.g. Acme Coffee Roasters" onChange={(e) => setName(e.target.value)} required /></label>
        <label>Business phone number<input value={phone} placeholder="e.g. +12125550101" onChange={(e) => setPhone(e.target.value)} required /></label>
        {error && <div className="formError">{error}</div>}
        <button className="primaryBtn" disabled={busy} type="submit">{busy ? 'Creating…' : 'Create workspace'} {!busy && <Icon name="chevron" size={13}/>}</button>
      </form>
      <small className="onboardingHint">Use a real number in E.164 format (with country code) — Telephony webhooks route inbound missed calls to it.</small>

      {recent.length > 0 && (
        <>
          <div className="onboardingDivider"><span>or return to a saved workspace</span></div>
          <div className="savedWorkspaces">
            {recent.map(w => (
              <button key={w.id} className="accountRow" onClick={() => onSignIn(w.id)} disabled={busy || findBusy}>
                <span className="accountIcon"><Icon name="grid" size={14}/></span>
                <span className="accountMeta"><span className="accountName">{w.name}</span><span className="accountPhone">{w.phone_number}</span></span>
                <Icon name="chevron" size={14}/>
              </button>
            ))}
          </div>
        </>
      )}

      <div className="onboardingDivider"><span>own a business already?</span></div>
      {findOpen ? (
        <form className="findForm" onSubmit={(e) => { e.preventDefault(); onFindByPhone(findPhone); }}>
          <label>Business phone number<input value={findPhone} placeholder="e.g. +12125550101" onChange={(e) => setFindPhone(e.target.value)} required autoFocus /></label>
          <button className="outlineBtn" disabled={findBusy || busy} type="submit">{findBusy ? 'Looking up…' : 'Sign back in'} <Icon name="search" size={14}/></button>
        </form>
      ) : (
        <button className="findLink" onClick={() => setFindOpen(true)} disabled={busy || findBusy}><Icon name="search" size={14}/> Find my business by phone number</button>
      )}
    </div>
  </div>;
}

function StatCard({ title, value, delta, type, icon }: { title: string; value: string; delta: string; type: 'purple'|'blue'|'green'|'orange'; icon?: IconName }) {
  const up = delta.includes('↑');
  const glyph = icon ?? (type === 'green' ? 'check' : type === 'orange' ? 'follow' : 'phone');
  return <div className={`statCard ${type}`}><div className="statIcon"><Icon name={glyph} size={16}/></div><div className="statTitle">{title}</div><div className="statValue">{value}</div><div className={`delta ${up ? 'up' : 'down'}`}>{up ? <Icon name="arrowUp" size={12}/> : <Icon name="arrowDown" size={12}/>} {delta.replace('↑ ', '').replace('↓ ', '')}</div><span className="muted">from your call log</span></div>;
}

function Chart() {
  return <div className="chartWrap">
    <div className="chartGrid"><span>40</span><span>30</span><span>20</span><span>10</span><span>0</span></div>
    <svg viewBox="0 0 600 210" preserveAspectRatio="none" className="chartSvg">
      <path d="M10 176 C65 120, 90 155, 140 105 S215 165, 255 115 S320 78, 360 108 S430 145, 470 96 S535 75, 590 18" className="line purple"/>
      <path d="M10 184 C70 172, 80 160, 140 150 S205 120, 255 145 S320 125, 365 135 S425 120, 470 110 S535 128, 590 94" className="line blue"/>
      <path d="M10 196 C65 170, 100 178, 145 188 S205 168, 255 182 S315 155, 365 142 S425 176, 470 160 S535 171, 590 145" className="line green"/>
    </svg>
    <div className="chartLabels">{['Day 1','Day 2','Day 3','Day 4','Day 5','Day 6','Day 7'].map(x=><span key={x}>{x}</span>)}</div>
  </div>;
}

function followUps(calls: CallJob[]) {
  return calls.filter(c => c.result?.needs_human_followup);
}

function Dashboard({ company, calls, onViewCall, onOpen, onConfigure }: { company: Company; calls: CallJob[]; onViewCall: () => void; onOpen: (id: number) => void; onConfigure: () => void }) {
  const total = calls.length;
  const done = calls.filter(c => c.status === 'completed' && c.result).length;
  const resolved = calls.filter(c => c.result?.resolved).length;
  const needsHuman = followUps(calls).length;
  const recent = calls.slice(0, 5);
  const open = followUps(calls).slice(0, 3);

  return <div className="page dashboardPage">
    <div className="pageIntro"><div><h2>Welcome to {company.name} 👋</h2><p>Here's what's happening with your calls today.</p></div></div>
    <div className="statsGrid">
      <StatCard title="Missed Calls" value={String(total)} delta={`Total`} type="purple" icon="phone"/>
      <StatCard title="Callbacks Completed" value={String(done)} delta={done > 0 ? '↑ Completed' : 'No data yet'} type="blue" icon="history"/>
      <StatCard title="Resolved" value={String(resolved)} delta={resolved > 0 ? '↑ Resolved' : 'No data yet'} type="green" icon="check"/>
      <StatCard title="Requires Follow-up" value={String(needsHuman)} delta={needsHuman > 0 ? '↓ Needs attention' : 'All clear'} type="orange" icon="follow"/>
    </div>
    <div className="dashboardGrid">
      <section className="panel recentPanel"><div className="panelHead"><h3>Recent Missed Calls</h3><button className="textBtn" onClick={onViewCall}>View all</button></div>{recent.length === 0 ? <div className="emptyInline">No missed-call events yet.</div> : <>
        <div className="desktopOnly tableScroll"><table><thead><tr><th>Caller</th><th>Received</th><th>Status</th></tr></thead><tbody>{recent.map(c => <tr key={c.id}><td><span className="caller"><span className="tinyPhone"><Icon name="phone" size={11}/></span>{c.caller_number}</span></td><td>{toLocalDate(c.created_at)}</td><td><Status>{followUpLabel(c)}</Status></td></tr>)}</tbody></table></div>
        <div className="mobileList">{recent.map(c => <button className="mobileCallCard" key={c.id} onClick={() => onOpen(c.id)}><span className="mobileCallIcon"><Icon name="phone" size={14}/></span><span className="mobileCallMain"><strong>{c.caller_number}</strong><small>{toLocalDate(c.created_at)}</small></span><Status>{followUpLabel(c)}</Status><Icon name="chevron" size={15}/></button>)}</div>
      </>}</section>
      <section className="panel chartPanel"><div className="panelHead"><h3>Callback Performance</h3><span className="selectBtn">Last 7 days</span></div><Chart/><div className="legend"><span><i className="dot purpleDot"/> Missed Calls</span><span><i className="dot blueDot"/> Completed</span><span><i className="dot greenDot"/> Resolved</span></div></section>
    </div>
    <div className="dashboardGrid bottomGrid">
      <section className="panel"><div className="panelHead"><h3>Follow-up Cases</h3><button className="textBtn" onClick={() => onOpen(0)}>View all</button></div>{open.length === 0 ? <div className="emptyInline">Nothing needs human attention right now.</div> : <div className="mobileList compactList">{open.map(c => <div className="followCard" key={c.id}><strong>{c.caller_number}</strong><span>{c.result?.question_asked || 'Unanswered question'}</span><small>{toLocalDate(c.created_at)}</small><Status>Requires Follow-up</Status></div>)}</div>}</section>
      <section className="panel phonePanel"><div className="panelHead"><h3>Your Phone Number</h3></div><div className="phoneNumber">{company.phone_number}</div><Status>Registered</Status><div className="provider"><span>CALL-E + Telnyx</span><button className="outlineBtn" onClick={onConfigure}>Configure <Icon name="settings" size={13}/></button></div></section>
    </div>
  </div>;
}

function MissedCalls({ calls, onOpen, onRefresh, refreshing }: { calls: CallJob[]; onOpen: (id: number) => void; onRefresh: () => void; refreshing: boolean }) {
  return <div className="page"><div className="pageTitleRow"><div><h2>Missed Calls</h2><p>Monitor real missed-call events and callback progress.</p></div><button className="primaryBtn" onClick={onRefresh} disabled={refreshing}><Icon name="refresh" size={16}/> {refreshing ? 'Refreshing…' : 'Refresh'}</button></div><section className="panel">{calls.length === 0 ? <div className="emptyState"><div className="emptyIcon"><Icon name="phone" size={28}/></div><h3>No missed calls yet</h3><p>Telnyx webhooks enqueue a callback here when a real customer call is missed. You can also create a test job from the API.</p></div> : <>
      <div className="desktopOnly tableScroll"><table className="fullTable"><thead><tr><th>Caller</th><th>Received</th><th>Status</th><th>Action</th></tr></thead><tbody>{calls.map(c => <tr key={c.id}><td><strong>{c.caller_number}</strong></td><td>{toLocalDate(c.created_at)}</td><td><Status>{followUpLabel(c)}</Status></td><td><button className="linkBtn" onClick={() => onOpen(c.id)}>View</button></td></tr>)}</tbody></table></div>
      <div className="mobileList pageList">{calls.map(c => <button className="dataCard" key={c.id} onClick={() => onOpen(c.id)}><div className="dataCardTop"><span><strong>{c.caller_number}</strong><small>{toLocalDate(c.created_at)}</small></span><Status>{followUpLabel(c)}</Status></div><span className="cardAction">View call <Icon name="external" size={13}/></span></button>)}</div>
    </>}</section></div>;
}

function CallHistory({ calls, onOpen }: { calls: CallJob[]; onOpen: (id: number) => void }) {
  return <div className="page"><div className="pageTitleRow"><div><h2>Call History</h2><p>View all your callback interactions and results.</p></div></div><section className="panel">{calls.length === 0 ? <div className="emptyState"><div className="emptyIcon"><Icon name="history" size={28}/></div><h3>No callbacks yet</h3><p>Completed AI callbacks with their structured results will appear here.</p></div> :
    <div className="tableScroll"><table className="fullTable"><thead><tr><th>Caller</th><th>Callback Time</th><th>Resolution</th><th>Status</th><th>Action</th></tr></thead><tbody>{calls.map(c => <tr key={c.id}><td>{c.caller_number}</td><td>{toLocalDate(c.created_at)}</td><td>{followUpLabel(c)}</td><td><Status>{statusLabel[c.status] ?? c.status}</Status></td><td><button className="linkBtn" onClick={() => onOpen(c.id)}>View</button></td></tr>)}</tbody></table></div>
      }</section></div>;
}

function FollowUpCases({ calls, onOpen }: { calls: CallJob[]; onOpen: (id: number) => void }) {
  const items = followUps(calls);
  return <div className="page"><div className="pageTitleRow"><div><h2>Follow-up Cases</h2><p>Track callbacks that need human attention.</p></div></div><section className="panel">{items.length === 0 ? <div className="emptyState"><div className="emptyIcon"><Icon name="follow" size={28}/></div><h3>No follow-ups needed</h3><p>Callbacks that the AI couldn't resolve will be listed here.</p></div> : <div className="tableScroll"><table className="fullTable"><thead><tr><th>Caller</th><th>Question</th><th>Received</th><th>Status</th></tr></thead><tbody>{items.map(c => <tr key={c.id} onClick={() => onOpen(c.id)} style={{ cursor: 'pointer' }}><td>{c.caller_number}</td><td>{c.result?.question_asked || '—'}</td><td>{toLocalDate(c.created_at)}</td><td><Status>Requires Follow-up</Status></td></tr>)}</tbody></table></div>}</section></div>;
}

function CallDetail({ jobId, onBack }: { jobId: number; onBack: () => void }) {
  const [job, setJob] = useState<CallJob | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    api.getCall(jobId)
      .then(j => { if (alive) setJob(j); })
      .catch(e => { if (alive) setError(String(e.message || e)); });
    return () => { alive = false; };
  }, [jobId]);

  if (error) return <div className="page"><section className="emptyState panel"><div className="emptyIcon"><Icon name="cloud" size={28}/></div><h3>Couldn't load this call</h3><p>{error}</p><button className="outlineBtn" onClick={onBack}>Back</button></section></div>;
  if (!job) return <div className="page"><LoadingState/></div>;

  return <div className="page"><div className="detailTop"><button className="backBtn" onClick={onBack}><Icon name="back" size={17}/> Back</button></div>
    <section className="callHero panel"><div className="bigPhone"><Icon name="phone" size={25}/></div><div><h2>{job.caller_number}</h2><p>{toLocalDate(job.created_at)}</p></div><div className="heroMeta"><span>Status</span><Status>{followUpLabel(job)}</Status></div></section>
    <div className="detailGrid"><section className="panel"><h3>Call Summary</h3><div className="summaryItem"><label>Customer Question</label><p>{job.result?.question_asked || 'No structured result received yet.'}</p></div><div className="summaryItem"><label>AI Answer Provided</label><p>{job.result?.answer_given || '—'}</p></div><div className="summaryItem"><label>Resolution</label><p><Status>{followUpLabel(job)}</Status></p></div><div className="summaryItem"><label>Follow-up Required</label><p>{job.result?.needs_human_followup ? 'Yes' : 'No'}</p></div>{job.result?.transcript_url ? <div className="summaryItem"><label>Transcript</label><p><a href={job.result.transcript_url} target="_blank" rel="noreferrer">{job.result.transcript_url} <Icon name="external" size={12}/></a></p></div> : null}</section>
      <section className="sideDetail"><div className="panel"><h3>Call Timeline</h3><div className="timeline">
        <div className="timelineItem"><span className="timelineDot"/><div><strong>Missed call received</strong><small>{toLocalDate(job.created_at) || '—'}</small></div></div>
        <div className="timelineItem"><span className="timelineDot"/><div><strong>AI callback {job.status === 'completed' ? 'completed' : job.status}</strong><small>{job.status === 'completed' ? 'Result stored' : '—'}</small></div></div>
      </div></div></section>
    </div>
  </div>;
}

function KnowledgeBase({ documents, companyId, onUpload, uploading }: { documents: ApiDocument[]; companyId: number; onUpload: (file: File) => void; uploading: boolean }) {
  const fileRef = useRef<HTMLInputElement>(null);
  return <div className="page"><div className="pageTitleRow"><div><h2>Knowledge Base</h2><p>Upload and manage your business knowledge and documents.</p></div><button className="primaryBtn" disabled={uploading} onClick={() => fileRef.current?.click()}><Icon name="upload" size={16}/> {uploading ? 'Uploading…' : 'Upload Document'}</button><input ref={fileRef} type="file" accept=".txt,.md,.csv" hidden onChange={(e) => { const f = e.target.files?.[0]; if (f) onUpload(f); e.target.value = ''; }} /></div><section className="panel">{documents.length === 0 ? <div className="emptyState"><div className="emptyIcon"><Icon name="book" size={28}/></div><h3>No knowledge documents yet</h3><p>Upload FAQs, policies or product info. Denwa chunks + embeds them and uses only this verified content when answering callbacks.</p></div> : <>
      <div className="desktopOnly tableScroll"><table className="fullTable"><thead><tr><th>Document Name</th><th>Status</th><th>Chunks</th><th>Uploaded</th></tr></thead><tbody>{documents.map(d => <tr key={d.id}><td><strong>{d.filename}</strong></td><td><Status>{d.status}</Status></td><td>{d.chunks_count}</td><td>{toLocalDate(d.uploaded_at)}</td></tr>)}</tbody></table></div>
      <div className="mobileList pageList">{documents.map(d => <div className="documentCard" key={d.id}><div><strong>{d.filename}</strong><small>Uploaded {toLocalDate(d.uploaded_at)}</small></div><div className="documentMeta"><span><b>Chunks</b>{d.chunks_count}</span><Status>{d.status}</Status></div></div>)}</div>
    </>}</section><div className="infoBanner"><div className="infoIcon"><Icon name="brain" size={19}/></div><div><strong>Grounded AI answers</strong><p>Denwa answers from approved company knowledge only. Unsupported questions are routed to human follow-up.</p></div></div></div>;
}

function GenericPage({ title, desc, icon }: { title: string; desc: string; icon: IconName }) {
  return <div className="page"><div className="pageTitleRow"><div><h2>{title}</h2><p>{desc}</p></div></div><section className="emptyState panel"><div className="emptyIcon"><Icon name={icon} size={28}/></div><h3>{title} workspace</h3><p>This area is part of the Denwa roadmap — the rest of the app is live with your real data.</p></section></div>;
}

function ProviderStatus({ title, desc }: { title: string; desc: string }) {
  const [cfg, setCfg] = useState<ConfigStatus | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const load = useCallback(() => {
    setErr(null);
    api.getConfigStatus().then(setCfg).catch(e => setErr(String((e as Error).message || e)));
  }, []);
  useEffect(() => { load(); }, [load]);

  if (err) return <div className="page"><div className="pageTitleRow"><div><h2>{title}</h2><p>{desc}</p></div></div><section className="emptyState panel"><div className="emptyIcon"><Icon name="cloud" size={28}/></div><h3>Couldn't load provider status</h3><p>{err}</p><button className="outlineBtn" onClick={load}>Retry <Icon name="refresh" size={15}/></button></section></div>;
  if (!cfg) return <div className="page"><div className="pageTitleRow"><div><h2>{title}</h2><p>{desc}</p></div></div><LoadingState /></div>;

  const providers: { name: string; icon: IconName; ok: boolean; status: string; note: string; detail: string }[] = [
    { name: 'CALL-E', icon: 'phone', ok: cfg.call_e_configured, status: cfg.call_e_configured ? 'Connected' : 'No API key', note: 'Outbound AI callback dialer', detail: cfg.call_e_base_url },
    { name: 'Telnyx', icon: 'numbers', ok: cfg.telnyx_configured, status: cfg.telnyx_configured ? 'Connected' : 'Not connected', note: 'Inbound missed-call webhooks', detail: cfg.signature_check_enabled ? 'Ed25519 signature verification on' : 'Signature check skipped (dev)' },
    { name: 'Groq', icon: 'brain', ok: cfg.groq_configured, status: cfg.groq_configured ? 'Connected' : 'Fallback mode', note: 'Answer task condensing', detail: cfg.groq_configured ? 'condenses retrieved knowledge' : 'deterministic template fallback' },
  ];

  return <div className="page">
    <div className="pageTitleRow"><div><h2>{title}</h2><p>{desc}</p></div></div>
    <section className="panel phonePanel">
      <div className="panelHead"><h3>Business Number</h3></div>
      <div className="phoneNumber">{cfg.business_phone_number || 'Not set in backend/.env'}</div>
      {cfg.business_phone_registered ? <Status>Registered</Status> : <Status>Not registered</Status>}
      <div className="provider"><span>{cfg.business_phone_registered
        ? 'Inbound webhooks route missed calls to this workspace.'
        : <>This workspace isn't attached to the number yet — sign in with that number to register it.</>}</span></div>
    </section>
    <section className="panel">
      <div className="panelHead"><h3>Providers</h3></div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {providers.map(p => (
          <div className="providerRow" key={p.name}>
            <span className="providerIcon"><Icon name={p.icon} size={15}/></span>
            <span className="providerBody"><strong>{p.name}</strong><small>{p.note} — {p.detail}</small></span>
            <span className={`status status-${p.ok ? 'connected' : 'not-connected'}`}>{p.status}</span>
          </div>
        ))}
        <div className="providerRow">
          <span className="providerIcon"><Icon name="settings" size={15}/></span>
          <span className="providerBody"><strong>Callback worker</strong><small>Background job loop that dials CALL-E</small></span>
          <span className={`status status-${cfg.worker_enabled ? 'connected' : 'not-connected'}`}>{cfg.worker_enabled ? 'Running' : 'Disabled'}</span>
        </div>
      </div>
      <small className="onboardingHint">Provider credentials live in <code>backend/.env</code>. Secret values are never exposed here.</small>
    </section>
  </div>;
}

type Toast = { kind: 'success' | 'error'; text: string };

function App() {
  const [companyId, setCompanyIdState] = useState<number | null>(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? Number(raw) : null;
  });
  const setCompanyId = useCallback((id: number | null) => {
    setCompanyIdState(id);
    if (id === null) localStorage.removeItem(STORAGE_KEY);
    else localStorage.setItem(STORAGE_KEY, String(id));
  }, []);

  const [company, setCompany] = useState<Company | null>(null);
  const [calls, setCalls] = useState<CallJob[]>([]);
  const [documents, setDocuments] = useState<ApiDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<Toast | null>(null);
  const [onboardingBusy, setOnboardingBusy] = useState(false);
  const [onboardingError, setOnboardingError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  const [active, setActive] = useState('Dashboard');
  const [detailId, setDetailId] = useState<number | null>(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [recent, setRecent] = useState<SavedCompany[]>(readRecent);
  const [findBusy, setFindBusy] = useState(false);

  const rememberCompany = useCallback((comp: Company) => {
    setRecent(prev => {
      const next = [{ id: comp.id, name: comp.name, phone_number: comp.phone_number }, ...prev.filter(p => p.id !== comp.id)];
      writeRecent(next);
      return next;
    });
  }, []);

  useEffect(() => {
    if (!notice) return;
    const t = setTimeout(() => setNotice(null), 4000);
    return () => clearTimeout(t);
  }, [notice]);

  const refreshData = useCallback(async (showBusy = true) => {
    if (companyId === null) return;
    if (showBusy) setRefreshing(true);
    try {
      const [callsRes, docsRes] = await Promise.all([
        api.listCalls(companyId),
        api.listDocuments(companyId),
      ]);
      setCalls(callsRes);
      setDocuments(docsRes);
      setError(null);
    } catch (e) {
      setError(String((e as Error).message || e));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [companyId]);

  useEffect(() => {
    if (companyId === null) {
      setLoading(false);
      return;
    }
    setLoading(true);
    api.getCompany(companyId)
      .then(comp => {
        setCompany(comp);
        rememberCompany(comp);
        return refreshData(true);
      })
      .then(() => setLoading(false))
      .catch(e => {
        setLoading(false);
        setError(String((e as Error).message || e));
        setCompanyId(null); // unknown company -> back to onboarding
      });
  }, [companyId, refreshData, rememberCompany, setCompanyId]);

  const createWorkspace = useCallback(async (name: string, phone: string) => {
    setOnboardingBusy(true);
    setOnboardingError(null);
    try {
      const comp = await api.createCompany(name.trim(), phone.trim());
      setCompany(comp);
      rememberCompany(comp);
      setCompanyId(comp.id);
    } catch (e) {
      setOnboardingError(String((e as Error).message || e));
    } finally {
      setOnboardingBusy(false);
    }
  }, [rememberCompany, setCompanyId]);

  const signInCompany = useCallback(async (id: number) => {
    setOnboardingError(null);
    try {
      const comp = await api.getCompany(id);
      setCompany(comp);
      rememberCompany(comp);
      setCompanyId(id);
    } catch (e) {
      setRecent(prev => {
        const next = prev.filter(p => p.id !== id);
        writeRecent(next);
        return next;
      });
      setOnboardingError('That saved workspace is no longer available.');
    }
  }, [rememberCompany, setCompanyId]);

  const findCompanyByPhone = useCallback(async (phone: string) => {
    setFindBusy(true);
    setOnboardingError(null);
    try {
      const comp = await api.findCompanyByPhone(phone.trim());
      setCompany(comp);
      rememberCompany(comp);
      setCompanyId(comp.id);
    } catch (e) {
      setOnboardingError(String((e as Error).message || e));
    } finally {
      setFindBusy(false);
    }
  }, [rememberCompany, setCompanyId]);

  const handleUpload = useCallback(async (file: File) => {
    if (companyId === null) return;
    setUploading(true);
    try {
      const doc = await api.uploadDocument(companyId, file);
      setNotice({ kind: 'success', text: `Uploaded "${doc.filename}" (${doc.chunks_count} chunks).` });
      await refreshData(false);
    } catch (e) {
      setNotice({ kind: 'error', text: `Upload failed: ${(e as Error).message}` });
    } finally {
      setUploading(false);
    }
  }, [companyId, refreshData]);

  const logout = useCallback(() => {
    setCompany(null);
    setCalls([]);
    setDocuments([]);
    setDetailId(null);
    setCompanyId(null);
  }, [setCompanyId]);

  const openCall = useCallback((id: number) => {
    if (id === 0) { setActive('Follow-up Cases'); setDetailId(null); }
    else setDetailId(id);
  }, []);

  const content = useMemo(() => {
    if (loading) return <LoadingState />;
    if (companyId === null || company === null) {
      return <Onboarding onCreate={createWorkspace} busy={onboardingBusy} error={onboardingError} onFindByPhone={findCompanyByPhone} findBusy={findBusy} recent={recent} onSignIn={signInCompany} />;
    }
    if (error) return <ErrorState message={error} onRetry={() => refreshData(true)} />;
    if (detailId !== null) return <CallDetail jobId={detailId} onBack={() => setDetailId(null)} />;
    switch (active) {
      case 'Dashboard': return <Dashboard company={company} calls={calls} onViewCall={() => { setActive('Missed Calls'); }} onOpen={openCall} onConfigure={() => { setActive('Settings'); setDetailId(null); }} />;
      case 'Missed Calls': return <MissedCalls calls={calls} onOpen={setDetailId} onRefresh={() => refreshData(true)} refreshing={refreshing} />;
      case 'Call History': return <CallHistory calls={calls} onOpen={setDetailId} />;
      case 'Knowledge Base': return <KnowledgeBase documents={documents} companyId={companyId} onUpload={handleUpload} uploading={uploading} />;
      case 'Follow-up Cases': return <FollowUpCases calls={calls} onOpen={setDetailId} />;
      case 'Phone Numbers': return <ProviderStatus title="Phone Numbers" desc="Connect and monitor the real business number used by Denwa." />;
      case 'Analytics': return <GenericPage title="Analytics" desc="Measure missed calls, callbacks, resolution and follow-up performance." icon="chart" />;
      case 'Settings': return <ProviderStatus title="Settings" desc="Business, provider and application configuration." />;
      case 'Team': return <GenericPage title="Team" desc="Manage the people who can operate this Denwa workspace." icon="team" />;
      default: return <Dashboard company={company} calls={calls} onViewCall={() => setActive('Missed Calls')} onOpen={openCall} onConfigure={() => { setActive('Settings'); setDetailId(null); }} />;
    }
  }, [loading, companyId, company, error, detailId, active, calls, documents, refreshing, uploading, onboardingBusy, onboardingError, findBusy, recent, openCall, refreshData, handleUpload, createWorkspace, signInCompany, findCompanyByPhone]);

  return <div className="app">
    {notice && <div className={`toast toast-${notice.kind}`}><span>{notice.text}</span><button onClick={() => setNotice(null)}><Icon name="close" size={13}/></button></div>}
    {companyId === null ? (
      <main className="main">{content}</main>
    ) : (
      <>
        <Sidebar active={detailId !== null ? 'Missed Calls' : active} setActive={(v) => { setActive(v); setDetailId(null); }} open={mobileOpen} onClose={() => setMobileOpen(false)} company={company} />
        <main className="main"><Header onMenu={() => setMobileOpen(true)} active={detailId !== null ? 'Missed Call Detail' : active} onLogout={logout} />{content}</main>
      </>
    )}
  </div>;
}

const rootEl = document.getElementById('root')!;
const root = createRoot(rootEl);
root.render(<React.StrictMode><App /></React.StrictMode>);
if (import.meta.hot) {
  import.meta.hot.dispose(() => root.unmount());
}