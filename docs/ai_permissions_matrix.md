# Copilot permissions

| Capability | Employee | Manager | Admin |
| --- | --- | --- | --- |
| Policy library | Read | Read | Read |
| Project catalog | Read | Read | Read |
| Employee/skill/assignment SQL | Own rows | Self + direct reports | All safe rows |
| View generated SQL | Hidden | Yes | Yes |
| Bank/PAN/password/payroll through AI | Blocked | Blocked | Blocked |
| Leave balance | Self | Self | Self |
| Submit leave / create ticket | Self | Self | Self |
| Approve/reject leave | Denied | Direct reports | Allowed by existing API |
| Create announcement | Denied | Allowed | Allowed |
| Assign employee to project | Denied | Direct reports | Allowed |
| Create project | Denied | Denied through AI | Allowed |
| Assign/update ticket | Denied | Existing API rules | Existing API rules |
| Policy uploads | Ordinary HRMS screens | Ordinary HRMS screens | Ordinary HRMS screens |
| Audit history | Own interactions | Own interactions | Own interactions |

Ticket management retains the starter's organization-wide manager permissions. This is deliberately stated rather than implying that every inherited HRMS feature is team-scoped. The copilot adds team checks specifically for leave decisions and project assignment. A production rollout should review every inherited endpoint, including finance and employee lifecycle routes, separately.

Role values and user IDs supplied in chat are never accepted as identity. Login/JWT authentication supplies the actor. Every write tool requires a separate account-bound confirmation. Employees cannot gain capabilities by selecting a different assistant mode.

Request Readiness always analyzes the signed-in user, including when the actor is a manager or admin. There is no client-supplied employee ID. Analyze is read-only for business tables; prepare writes only proposal/audit metadata, and confirmation uses the existing leave API.
