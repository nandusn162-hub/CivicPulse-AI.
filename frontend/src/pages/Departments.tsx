import React, { useState, useEffect } from 'react';
import { Building2, Mail, Phone, User, CheckCircle2, ShieldAlert } from 'lucide-react';
import { fetchDepartments, fetchComplaints, DepartmentInfo, ComplaintData } from '../lib/api';

export default function DepartmentsPage() {
  const [departments, setDepartments] = useState<DepartmentInfo[]>([]);
  const [complaints, setComplaints] = useState<ComplaintData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [deptList, compList] = await Promise.all([
        fetchDepartments().catch(() => []),
        fetchComplaints({ limit: 100 }).catch(() => []),
      ]);
      setDepartments(deptList);
      setComplaints(compList);
    } catch (err) {
      console.error('Error fetching departments', err);
    } finally {
      setLoading(false);
    }
  };

  const getComplaintCountForDept = (categories: string[]) => {
    return complaints.filter((c) => categories.includes(c.category)).length;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <Building2 size={24} className="text-teal-600" />
          <span>Municipal Service Departments</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Authorized civic departments managing field repair work orders and grievance resolution across wards.
        </p>
      </div>

      {loading ? (
        <div className="py-24 text-center text-slate-400">
          <div className="w-8 h-8 border-3 border-teal-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          Loading municipal departments...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {departments.map((dept) => {
            const count = getComplaintCountForDept(dept.categories);
            return (
              <div
                key={dept.id}
                className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs space-y-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-100 text-slate-600">
                      {dept.code}
                    </span>
                    <h3 className="text-base font-bold text-slate-900 leading-snug">{dept.name}</h3>
                  </div>
                  <div className="p-2 rounded-xl bg-teal-50 text-teal-700">
                    <Building2 size={18} />
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-100 space-y-2 text-xs">
                  <div className="flex items-center gap-2 text-slate-600">
                    <User size={14} className="text-slate-400 shrink-0" />
                    <span>Head: <strong className="text-slate-800">{dept.head}</strong></span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-600">
                    <Mail size={14} className="text-slate-400 shrink-0" />
                    <span className="font-mono text-[11px]">{dept.email}</span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-600">
                    <Phone size={14} className="text-slate-400 shrink-0" />
                    <span className="font-mono text-[11px]">{dept.phone}</span>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                  <div className="text-[11px] text-slate-400 font-medium">Active Incidents</div>
                  <div className="text-sm font-black text-slate-900 bg-slate-100 px-2.5 py-0.5 rounded-lg">
                    {count}
                  </div>
                </div>

                <div className="flex flex-wrap gap-1.5 pt-1">
                  {dept.categories.map((c) => (
                    <span
                      key={c}
                      className="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-teal-50/80 text-teal-700 border border-teal-100 capitalize"
                    >
                      {c.replace('_', ' ')}
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
