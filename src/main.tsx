import React, { useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

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

const calls = [
  { caller: '+1 (555) 123-4567', business: '+1 (212) 555-0101', time: 'May 24, 10:21 AM', duration: '04:32', status: 'Processing' },
  { caller: '+1 (555) 987-6543', business: '+1 (212) 555-0101', time: 'May 24, 09:15 AM', duration: '03:12', status: 'Completed' },
  { caller: '+1 (555) 246-8101', business: '+1 (212) 555-0101', time: 'May 24, 08:42 AM', duration: '02:45', status: 'Completed' },
  { caller: '+1 (555) 135-7911', business: '+1 (212) 555-0101', time: 'May 24, 07:33 AM', duration: '05:01', status: 'Completed' },
  { caller: '+1 (555) 864-2000', business: '+1 (212) 555-0101', time: 'May 24, 06:11 AM', duration: '01:22', status: 'Requires Follow-up' },
];

const history = [
  { caller: '+1 (555) 123-4567', time: 'May 24, 10:23 AM', duration: '04:32', resolution: 'Answered', status: 'Completed' },
  { caller: '+1 (555) 987-6543', time: 'May 24, 09:10 AM', duration: '03:12', resolution: 'Answered', status: 'Completed' },
  { caller: '+1 (555) 246-8101', time: 'May 24, 08:45 AM', duration: '02:45', resolution: 'Requires Follow-up', status: 'Completed' },
  { caller: '+1 (555) 135-7911', time: 'May 24, 07:36 AM', duration: '05:01', resolution: 'Answered', status: 'Completed' },
  { caller: '+1 (555) 864-2000', time: 'May 24, 06:14 AM', duration: '01:22', resolution: 'Requires Follow-up', status: 'Requires Follow-up' },
  { caller: '+1 (555) 678-1111', time: 'May 23, 02:15 PM', duration: '—', resolution: '—', status: 'Open' },
];

const documents = [
  ['General FAQs', 'FAQ', 'Active', '45', 'May 20, 2025'],
  ['Pricing Guide 2025', 'Pricing', 'Active', '32', 'May 18, 2025'],
  ['Return & Refund Policy', 'Policy', 'Active', '28', 'May 15, 2025'],
  ['Shipping Information', 'Operations', 'Active', '18', 'May 10, 2025'],
  ['Product Catalog', 'Operations', 'Active', '55', 'May 08, 2025'],
];

function Logo() {
  return <div className="logoMark"><span>⌁</span><b>Denwa</b></div>;
}

function Sidebar({ active, setActive, open, onClose }: { active: string; setActive: (v: string) => void; open: boolean; onClose: () => void }) {
  return <>
    {open && <div className="mobileOverlay" onClick={onClose} />}
    <aside className={`sidebar ${open ? 'open' : ''}`}>
      <div className="brand"><Logo /><button className="mobileClose" onClick={onClose}><Icon name="close" size={20}/></button></div>
      <div className="agentLabel">AI Callback Support Agent</div>
      <nav>
        {navItems.map(item => <button key={item.label} className={`navItem ${active === item.label ? 'active' : ''}`} onClick={() => { setActive(item.label); onClose(); }}><Icon name={item.icon}/><span>{item.label}</span></button>)}
      </nav>
      <div className="accountCard">
        <div className="avatar">A</div>
        <div><strong>Acme Company</strong><small>Owner</small></div>
        <Icon name="chevron" size={16}/>
      </div>
    </aside>
  </>;
}

function Header({ onMenu, active }: { onMenu: () => void; active: string }) {
  return <header className="topbar">
    <button className="menuBtn" onClick={onMenu}><Icon name="menu" size={21}/></button>
    <div><div className="crumb">Denwa <span>/</span> {active}</div><h1>{active}</h1></div>
    <div className="headerRight"><div className="datePill"><Icon name="calendar" size={16}/> May 18 – May 24, 2025 <Icon name="chevron" size={14}/></div><div className="userDot">A</div></div>
  </header>;
}

function Status({ children }: { children: string }) {
  const key = children.toLowerCase();
  return <span className={`status status-${key.replaceAll(' ', '-').replaceAll('—','')}`}>{children}</span>;
}

function StatCard({ title, value, delta, type }: { title: string; value: string; delta: string; type: 'purple'|'blue'|'green'|'orange' }) {
  const up = delta.includes('↑');
  return <div className={`statCard ${type}`}><div className="statIcon"><Icon name={type === 'green' ? 'check' : type === 'orange' ? 'follow' : 'phone'} size={16}/></div><div className="statTitle">{title}</div><div className="statValue">{value}</div><div className={`delta ${up ? 'up' : 'down'}`}>{up ? <Icon name="arrowUp" size={12}/> : <Icon name="arrowDown" size={12}/>} {delta.replace('↑ ','').replace('↓ ','')}</div><span className="muted">vs last 7 days</span></div>;
}

function Chart() {
  return <div className="chartWrap">
    <div className="chartGrid"><span>40</span><span>30</span><span>20</span><span>10</span><span>0</span></div>
    <svg viewBox="0 0 600 210" preserveAspectRatio="none" className="chartSvg">
      <path d="M10 176 C65 120, 90 155, 140 105 S215 165, 255 115 S320 78, 360 108 S430 145, 470 96 S535 75, 590 18" className="line purple"/>
      <path d="M10 184 C70 172, 80 160, 140 150 S205 120, 255 145 S320 125, 365 135 S425 120, 470 110 S535 128, 590 94" className="line blue"/>
      <path d="M10 196 C65 170, 100 178, 145 188 S205 168, 255 182 S315 155, 365 142 S425 176, 470 160 S535 171, 590 145" className="line green"/>
    </svg>
    <div className="chartLabels">{['May 18','May 19','May 20','May 21','May 22','May 23','May 24'].map(x=><span key={x}>{x}</span>)}</div>
  </div>;
}

function Dashboard({ onViewCall }: { onViewCall: () => void }) {
  return <div className="page dashboardPage">
    <div className="pageIntro"><div><h2>Good morning, Acme Company 👋</h2><p>Here's what's happening with your calls today.</p></div></div>
    <div className="statsGrid">
      <StatCard title="Missed Calls" value="24" delta="↑ 12%" type="purple"/>
      <StatCard title="Callbacks Completed" value="19" delta="↑ 8%" type="blue"/>
      <StatCard title="Resolved" value="14" delta="↑ 10%" type="green"/>
      <StatCard title="Requires Follow-up" value="5" delta="↓ 5%" type="orange"/>
    </div>
    <div className="dashboardGrid">
      <section className="panel recentPanel"><div className="panelHead"><h3>Recent Missed Calls</h3><button className="textBtn" onClick={onViewCall}>View all</button></div><div className="desktopOnly tableScroll"><table><thead><tr><th>Caller</th><th>Business Number</th><th>Time</th><th>Status</th></tr></thead><tbody>{calls.map(c=><tr key={c.caller}><td><span className="caller"><span className="tinyPhone"><Icon name="phone" size={11}/></span>{c.caller}</span></td><td>{c.business}</td><td>{c.time}</td><td><Status>{c.status}</Status></td></tr>)}</tbody></table></div><div className="mobileList">{calls.map(c=><button className="mobileCallCard" key={c.caller} onClick={onViewCall}><span className="mobileCallIcon"><Icon name="phone" size={14}/></span><span className="mobileCallMain"><strong>{c.caller}</strong><small>{c.time}</small></span><Status>{c.status}</Status><Icon name="chevron" size={15}/></button>)}</div></section>
      <section className="panel chartPanel"><div className="panelHead"><h3>Callback Performance</h3><button className="selectBtn">Last 7 days <Icon name="chevron" size={13}/></button></div><Chart/><div className="legend"><span><i className="dot purpleDot"/> Missed Calls</span><span><i className="dot blueDot"/> Callbacks</span><span><i className="dot greenDot"/> Resolved</span></div></section>
    </div>
    <div className="dashboardGrid bottomGrid">
      <section className="panel"><div className="panelHead"><h3>Follow-up Cases</h3><button className="textBtn">View all</button></div><div className="desktopOnly tableScroll"><table><thead><tr><th>Caller</th><th>Issue</th><th>Callback Time</th><th>Status</th></tr></thead><tbody><tr><td>+1 (555) 678-1111</td><td>Question about pricing</td><td>May 23, 02:15 PM</td><td><Status>Open</Status></td></tr><tr><td>+1 (555) 222-3333</td><td>Product availability</td><td>May 23, 11:42 AM</td><td><Status>Open</Status></td></tr><tr><td>+1 (555) 444-5555</td><td>Return & refund policy</td><td>May 22, 04:33 PM</td><td><Status>Open</Status></td></tr></tbody></table></div><div className="mobileList compactList"><div className="followCard"><strong>+1 (555) 678-1111</strong><span>Question about pricing</span><small>May 23, 02:15 PM</small><Status>Open</Status></div><div className="followCard"><strong>+1 (555) 222-3333</strong><span>Product availability</span><small>May 23, 11:42 AM</small><Status>Open</Status></div><div className="followCard"><strong>+1 (555) 444-5555</strong><span>Return & refund policy</span><small>May 22, 04:33 PM</small><Status>Open</Status></div></div></section>
      <section className="panel phonePanel"><div className="panelHead"><h3>Your Phone Number</h3></div><div className="phoneNumber">+1 (212) 555-0101</div><Status>Connected</Status><div className="provider"><span>Twilio</span><button className="outlineBtn">Manage Numbers <Icon name="chevron" size={13}/></button></div></section>
    </div>
  </div>;
}

function MissedCalls({ onOpen }: { onOpen: () => void }) {
  return <div className="page"><div className="pageTitleRow"><div><h2>Missed Calls</h2><p>Monitor real missed-call events and callback progress.</p></div><button className="primaryBtn"><Icon name="refresh" size={16}/> Refresh</button></div><section className="panel"><div className="toolbar"><div className="searchBox"><Icon name="search" size={17}/><input placeholder="Search by phone number or question..."/></div><button className="selectBtn">May 18 – May 24, 2025 <Icon name="calendar" size={14}/></button><button className="selectBtn">All Status <Icon name="chevron" size={13}/></button></div><div className="desktopOnly tableScroll"><table className="fullTable"><thead><tr><th>Caller</th><th>Received</th><th>Callback</th><th>Duration</th><th>Status</th><th>Action</th></tr></thead><tbody>{calls.map(c=><tr key={c.caller}><td><strong>{c.caller}</strong><small>{c.business}</small></td><td>{c.time}</td><td>{c.status === 'Processing' ? 'In progress' : 'Completed'}</td><td>{c.duration}</td><td><Status>{c.status}</Status></td><td><button className="linkBtn" onClick={onOpen}>View</button></td></tr>)}</tbody></table></div><div className="mobileList pageList">{calls.map(c=><button className="dataCard" key={c.caller} onClick={onOpen}><div className="dataCardTop"><span><strong>{c.caller}</strong><small>{c.business}</small></span><Status>{c.status}</Status></div><div className="dataCardMeta"><span><b>Received</b>{c.time}</span><span><b>Callback</b>{c.status === 'Processing' ? 'In progress' : 'Completed'}</span><span><b>Duration</b>{c.duration}</span></div><span className="cardAction">View call <Icon name="external" size={13}/></span></button>)}</div></section></div>;
}

function CallDetail({ onBack }: { onBack: () => void }) {
  return <div className="page"><div className="detailTop"><button className="backBtn" onClick={onBack}><Icon name="back" size={17}/> Back to Missed Calls</button><button className="primaryBtn">Mark as Reviewed <Icon name="chevron" size={13}/></button></div><section className="callHero panel"><div className="bigPhone"><Icon name="phone" size={25}/></div><div><h2>+1 (555) 123-4567</h2><p>May 24, 2025 at 10:21 AM</p></div><div className="heroMeta"><span>Status</span><Status>Completed</Status><span>Call Duration</span><strong>04:32</strong></div></section><div className="detailGrid"><section className="panel"><h3>Call Summary</h3><div className="summaryItem"><label>Customer Question</label><p>Do you have the 15-inch laptop in stock and what is the price?</p></div><div className="summaryItem"><label>AI Answer Provided</label><p>Yes, the 15-inch laptop is currently in stock. The price is $1,249.99 including tax.</p></div><div className="summaryItem"><label>Resolution</label><p><Status>Answered</Status></p></div><div className="summaryItem"><label>Follow-up Required</label><p>No</p></div><div className="confidence"><div><span>Confidence Score</span><strong>92%</strong></div><div className="progress"><i style={{width:'92%'}}/></div></div></section><section className="sideDetail"><div className="panel recording"><h3>Call Recording</h3><div className="player"><button><Icon name="play" size={15}/></button><span>0:00 / 4:32</span><div className="playerBar"><i/></div><span>◖</span><button className="iconBtn"><Icon name="download" size={17}/></button></div></div><div className="panel"><h3>Call Timeline</h3><Timeline/></div></section></div></div>;
}

function Timeline() { const items=[['Missed call received','May 24, 10:21 AM'],['Information retrieved','May 24, 10:21 AM'],['Callback initiated','May 24, 10:22 AM'],['Call connected','May 24, 10:23 AM'],['Call completed','May 24, 10:27 AM'],['Result stored','May 24, 10:27 AM']]; return <div className="timeline">{items.map(([a,b])=><div className="timelineItem" key={a}><span className="timelineDot"/><div><strong>{a}</strong><small>{b}</small></div></div>)}</div>; }

function CallHistory() {
  return <div className="page"><div className="pageTitleRow"><div><h2>Call History</h2><p>View all your callback interactions and results.</p></div><button className="outlineBtn"><Icon name="download" size={15}/> Export <Icon name="chevron" size={13}/></button></div><section className="panel"><div className="toolbar"><div className="searchBox"><Icon name="search" size={17}/><input placeholder="Search by phone number or question..."/></div><button className="selectBtn">May 18 – May 24, 2025 <Icon name="calendar" size={14}/></button><button className="selectBtn">All Status <Icon name="chevron" size={13}/></button></div><div className="desktopOnly tableScroll"><table className="fullTable"><thead><tr><th>Caller</th><th>Callback Time</th><th>Duration</th><th>Resolution</th><th>Status</th><th>Actions</th></tr></thead><tbody>{history.map((c,i)=><tr key={i}><td>{c.caller}</td><td>{c.time}</td><td>{c.duration}</td><td>{c.resolution}</td><td><Status>{c.status}</Status></td><td><button className="linkBtn">View</button> <button className="iconBtn"><Icon name="more" size={15}/></button></td></tr>)}</tbody></table></div><div className="mobileList pageList">{history.map((c,i)=><div className="historyCard" key={i}><div className="dataCardTop"><span><strong>{c.caller}</strong><small>{c.time}</small></span><Status>{c.status}</Status></div><div className="historyStats"><span><b>Duration</b>{c.duration}</span><span><b>Resolution</b>{c.resolution}</span></div><button className="cardAction">View details <Icon name="external" size={13}/></button></div>)}</div><div className="pagination"><span>Showing 1 to 6 of 24 results</span><div><button>‹</button><button className="current">1</button><button>2</button><button>3</button><button>4</button><button>…</button><button>›</button></div></div></section></div>;
}

function KnowledgeBase() {
  return <div className="page"><div className="pageTitleRow"><div><h2>Knowledge Base</h2><p>Upload and manage your business knowledge and documents.</p></div><button className="primaryBtn"><Icon name="upload" size={16}/> Upload Document</button></div><section className="panel"><div className="tabs"><button className="active">All Documents</button><button>FAQs</button><button>Pricing</button><button>Policies</button><button>Operations</button></div><div className="desktopOnly tableScroll"><table className="fullTable"><thead><tr><th>Document Name</th><th>Type</th><th>Status</th><th>Chunks</th><th>Last Updated</th><th>Actions</th></tr></thead><tbody>{documents.map(d=><tr key={d[0]}><td><strong>{d[0]}</strong></td><td>{d[1]}</td><td><Status>{d[2]}</Status></td><td>{d[3]}</td><td>{d[4]}</td><td><button className="iconBtn"><Icon name="more" size={15}/></button></td></tr>)}</tbody></table></div><div className="mobileList pageList">{documents.map(d=><div className="documentCard" key={d[0]}><div><strong>{d[0]}</strong><small>{d[1]} · Updated {d[4]}</small></div><div className="documentMeta"><span><b>Chunks</b>{d[3]}</span><Status>{d[2]}</Status><button className="iconBtn"><Icon name="more" size={15}/></button></div></div>)}</div></section><div className="infoBanner"><div className="infoIcon"><Icon name="brain" size={19}/></div><div><strong>Grounded AI answers</strong><p>Denwa should answer from approved company knowledge only. Unsupported questions are routed to human follow-up.</p></div></div></div>;
}

function GenericPage({ title, desc, icon }: { title: string; desc: string; icon: IconName }) {
  return <div className="page"><div className="pageTitleRow"><div><h2>{title}</h2><p>{desc}</p></div></div><section className="emptyState panel"><div className="emptyIcon"><Icon name={icon} size={28}/></div><h3>{title} workspace</h3><p>This screen is ready for backend/API integration. The shared frontend contract supports loading, empty, error and retry states.</p><button className="outlineBtn">Configure <Icon name="external" size={15}/></button></section></div>;
}

function App() {
  const [active, setActive] = useState('Dashboard');
  const [mobileOpen, setMobileOpen] = useState(false);
  const [detail, setDetail] = useState(false);
  const content = useMemo(() => {
    if (detail) return <CallDetail onBack={() => setDetail(false)} />;
    switch(active) {
      case 'Dashboard': return <Dashboard onViewCall={() => { setActive('Missed Calls'); setDetail(false); }} />;
      case 'Missed Calls': return <MissedCalls onOpen={() => setDetail(true)} />;
      case 'Call History': return <CallHistory />;
      case 'Knowledge Base': return <KnowledgeBase />;
      case 'Phone Numbers': return <GenericPage title="Phone Numbers" desc="Connect and monitor the real business number used by Denwa." icon="numbers" />;
      case 'Follow-up Cases': return <GenericPage title="Follow-up Cases" desc="Track callbacks that need human attention." icon="follow" />;
      case 'Analytics': return <GenericPage title="Analytics" desc="Measure missed calls, callbacks, resolution and follow-up performance." icon="chart" />;
      case 'Settings': return <GenericPage title="Settings" desc="Manage business, provider and application configuration." icon="settings" />;
      case 'Team': return <GenericPage title="Team" desc="Manage the people who can operate this Denwa workspace." icon="team" />;
      default: return <Dashboard onViewCall={() => setActive('Missed Calls')} />;
    }
  }, [active, detail]);
  return <div className="app"><Sidebar active={active} setActive={v => {setActive(v); setDetail(false);}} open={mobileOpen} onClose={() => setMobileOpen(false)} /><main className="main"><Header onMenu={() => setMobileOpen(true)} active={detail ? 'Missed Call Detail' : active}/>{content}</main></div>;
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);
