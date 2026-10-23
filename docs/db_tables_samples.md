# Database Schema Reference

- Database file: `backend/storage/hrms.db`
- Tables found: **20**
- Sample records are omitted from the public documentation.

## Tables

- `alembic_version`
- `announcements`
- `attendance_logs`
- `departments`
- `employee_documents`
- `employee_projects`
- `employee_skills`
- `employees`
- `holidays`
- `hr_policies`
- `job_history`
- `leave_balances`
- `leave_requests`
- `onboarding_tasks`
- `payroll_records`
- `poll_responses`
- `polls`
- `projects`
- `skills`
- `tickets`

## `alembic_version`

### Columns

| name | type | notnull | pk | default |
|---|---|---:|---:|---|
| `version_num` | `VARCHAR(32)` | 1 | 1 | `` |


## `announcements`

### Columns

| name | type | notnull | pk | default |
|---|---|---:|---:|---|
| `id` | `INTEGER` | 1 | 1 | `` |
| `title` | `VARCHAR(180)` | 1 | 0 | `` |
| `body` | `TEXT` | 1 | 0 | `` |
| `author_id` | `INTEGER` | 1 | 0 | `` |
| `created_at` | `DATETIME` | 1 | 0 | `CURRENT_TIMESTAMP` |


## `attendance_logs`

### Columns

| name | type | notnull | pk | default |
|---|---|---:|---:|---|
| `id` | `INTEGER` | 1 | 1 | `` |
| `employee_id` | `INTEGER` | 1 | 0 | `` |
| `date` | `DATE` | 1 | 0 | `` |
| `clock_in` | `TIME` | 0 | 0 | `` |
| `clock_out` | `TIME` | 0 | 0 | `` |
| `status` | `VARCHAR(7)` | 1 | 0 | `` |
| `work_mode` | `VARCHAR(20)` | 0 | 0 | `` |
| `punctuality` | `VARCHAR(20)` | 0 | 0 | `` |


## `departments`

### Columns

| name | type | notnull | pk | default |
|---|---|---:|---:|---|
| `id` | `INTEGER` | 1 | 1 | `` |
| `name` | `VARCHAR(120)` | 1 | 0 | `` |
| `location` | `VARCHAR(120)` | 1 | 0 | `` |


## `employee_documents`

### Columns

| name | type | notnull | pk | default |
|---|---|---:|---:|---|
| `id` | `INTEGER` | 1 | 1 | `` |
| `employee_id` | `INTEGER` | 1 | 0 | `` |
| `uploaded_by` | `INTEGER` | 0 | 0 | `` |
| `title` | `VARCHAR(220)` | 1 | 0 | `` |
| `document_type` | `VARCHAR(40)` | 1 | 0 | `` |
| `original_filename` | `VARCHAR(255)` | 1 | 0 | `` |
| `file_path` | `TEXT` | 1 | 0 | `` |
| `mime_type` | `VARCHAR(120)` | 1 | 0 | `` |
| `size_bytes` | `INTEGER` | 1 | 0 | `` |
| `checksum` | `VARCHAR(64)` | 1 | 0 | `` |
| `created_at` | `DATETIME` | 1 | 0 | `CURRENT_TIMESTAMP` |


## `employee_projects`

### Columns

| name | type | notnull | pk | default |
|---|---|---:|---:|---|
| `id` | `INTEGER` | 1 | 1 | `` |
| `employee_id` | `INTEGER` | 1 | 0 | `` |
| `project_id` | `INTEGER` | 1 | 0 | `` |
| `role_on_project` | `VARCHAR(120)` | 0 | 0 | `` |


## `employee_skills`

### Columns

| name | type | notnull | pk | default |
|---|---|---:|---:|---|
| `id` | `INTEGER` | 1 | 1 | `` |
| `employee_id` | `INTEGER` | 1 | 0 | `` |
| `skill_id` | `INTEGER` | 1 | 0 | `` |
| `level` | `VARCHAR(12)` | 1 | 0 | `` |


## `employees`

### Columns

| name | type | notnull | pk | default |
|---|---|---:|---:|---|
| `id` | `INTEGER` | 1 | 1 | `` |
| `name` | `VARCHAR(120)` | 1 | 0 | `` |
| `email` | `VARCHAR(255)` | 1 | 0 | `` |
| `hashed_password` | `VARCHAR(255)` | 1 | 0 | `` |
| `department_id` | `INTEGER` | 0 | 0 | `` |
| `manager_id` | `INTEGER` | 0 | 0 | `` |
| `role` | `VARCHAR(8)` | 1 | 0 | `` |
| `status` | `VARCHAR(8)` | 1 | 0 | `` |
| `joining_date` | `DATE` | 1 | 0 | `` |
| `phone` | `VARCHAR(20)` | 0 | 0 | `` |
| `address` | `VARCHAR(255)` | 0 | 0 | `` |
| `blood_type` | `VARCHAR(8)` | 0 | 0 | `` |
| `occupancy` | `VARCHAR(60)` | 0 | 0 | `` |
| `date_of_birth` | `DATE` | 0 | 0 | `` |
| `profile_photo_path` | `VARCHAR(255)` | 0 | 0 | `` |
| `profile_photo_mime` | `VARCHAR(64)` | 0 | 0 | `` |
| `current_salary_usd` | `NUMERIC(12, 2)` | 0 | 0 | `` |
| `bank_name` | `VARCHAR(120)` | 0 | 0 | `` |
| `bank_account_number` | `VARCHAR(34)` | 0 | 0 | `` |
| `bank_account_name` | `VARCHAR(120)` | 0 | 0 | `` |
| `bank_branch` | `VARCHAR(120)` | 0 | 0 | `` |
| `bank_ifsc` | `VARCHAR(20)` | 0 | 0 | `` |
| `pan_number` | `VARCHAR(20)` | 0 | 0 | `` |
| `pan_name` | `VARCHAR(120)` | 0 | 0 | `` |
| `pan_dob` | `DATE` | 0 | 0 | `` |


## `holidays`

### Columns

| name | type | notnull | pk | default |
|---|---|---:|---:|---|
| `id` | `INTEGER` | 1 | 1 | `` |
| `name` | `VARCHAR(120)` | 1 | 0 | `` |
| `date` | `DATE` | 1 | 0 | `` |


## `hr_policies`

### Columns

| name | type | notnull | pk | default |
|---|---|---:|---:|---|
| `id` | `INTEGER` | 1 | 1 | `` |
| `title` | `VARCHAR(220)` | 1 | 0 | `` |
| `content` | `TEXT` | 0 | 0 | `` |
| `category` | `VARCHAR(60)` | 1 | 0 | `` |
| `embedding` | `JSON` | 0 | 0 | `` |
| `original_filename` | `VARCHAR(255)` | 0 | 0 | `` |
| `file_path` | `TEXT` | 0 | 0 | `` |
| `mime_type` | `VARCHAR(100)` | 0 | 0 | `` |
| `size_bytes` | `INTEGER` | 0 | 0 | `` |
| `uploaded_by` | `INTEGER` | 0 | 0 | `` |
| `checksum` | `VARCHAR(64)` | 0 | 0 | `` |
| `created_at` | `DATETIME` | 1 | 0 | `CURRENT_TIMESTAMP` |


## `job_history`

### Columns

| name | type | notnull | pk | default |
|---|---|---:|---:|---|
| `id` | `INTEGER` | 1 | 1 | `` |
| `employee_id` | `INTEGER` | 1 | 0 | `` |
| `designation` | `VARCHAR(120)` | 1 | 0 | `` |
| `business_unit` | `VARCHAR(120)` | 1 | 0 | `` |
| `department` | `VARCHAR(120)` | 1 | 0 | `` |
| `start_date` | `DATE` | 1 | 0 | `` |
| `end_date` | `DATE` | 0 | 0 | `` |
| `is_current` | `BOOLEAN` | 1 | 0 | `` |


## `leave_balances`

### Columns

| name | type | notnull | pk | default |
|---|---|---:|---:|---|
| `id` | `INTEGER` | 1 | 1 | `` |
| `employee_id` | `INTEGER` | 1 | 0 | `` |
| `leave_type` | `VARCHAR(6)` | 1 | 0 | `` |
| `total` | `INTEGER` | 1 | 0 | `` |
| `used` | `INTEGER` | 1 | 0 | `` |
| `remaining` | `INTEGER` | 1 | 0 | `` |


## `leave_requests`

### Columns

| name | type | notnull | pk | default |
|---|---|---:|---:|---|
| `id` | `INTEGER` | 1 | 1 | `` |
| `employee_id` | `INTEGER` | 1 | 0 | `` |
| `leave_type` | `VARCHAR(6)` | 1 | 0 | `` |
| `start_date` | `DATE` | 1 | 0 | `` |
| `end_date` | `DATE` | 1 | 0 | `` |
| `reason` | `VARCHAR(500)` | 1 | 0 | `` |
| `is_half_day` | `BOOLEAN` | 1 | 0 | `0` |
| `half_day_period` | `VARCHAR(11)` | 0 | 0 | `` |
| `status` | `VARCHAR(8)` | 1 | 0 | `` |
| `approver_id` | `INTEGER` | 0 | 0 | `` |


## `onboarding_tasks`

### Columns

| name | type | notnull | pk | default |
|---|---|---:|---:|---|
| `id` | `INTEGER` | 1 | 1 | `` |
| `ticket_id` | `INTEGER` | 1 | 0 | `` |
| `task_name` | `VARCHAR(200)` | 1 | 0 | `` |
| `is_completed` | `BOOLEAN` | 1 | 0 | `` |
| `due_date` | `DATE` | 0 | 0 | `` |


## `payroll_records`

### Columns

| name | type | notnull | pk | default |
|---|---|---:|---:|---|
| `id` | `INTEGER` | 1 | 1 | `` |
| `employee_id` | `INTEGER` | 1 | 0 | `` |
| `month` | `DATE` | 1 | 0 | `` |
| `gross` | `FLOAT` | 1 | 0 | `` |
| `deductions` | `JSON` | 1 | 0 | `` |
| `net` | `FLOAT` | 1 | 0 | `` |
| `pan` | `VARCHAR(20)` | 1 | 0 | `` |
| `pf_uan` | `VARCHAR(30)` | 0 | 0 | `` |
| `esi_no` | `VARCHAR(30)` | 0 | 0 | `` |


## `poll_responses`

### Columns

| name | type | notnull | pk | default |
|---|---|---:|---:|---|
| `id` | `INTEGER` | 1 | 1 | `` |
| `poll_id` | `INTEGER` | 1 | 0 | `` |
| `employee_id` | `INTEGER` | 1 | 0 | `` |
| `option_index` | `INTEGER` | 1 | 0 | `` |


## `polls`

### Columns

| name | type | notnull | pk | default |
|---|---|---:|---:|---|
| `id` | `INTEGER` | 1 | 1 | `` |
| `question` | `VARCHAR(300)` | 1 | 0 | `` |
| `options` | `JSON` | 1 | 0 | `` |
| `created_by` | `INTEGER` | 1 | 0 | `` |
| `created_at` | `DATETIME` | 1 | 0 | `CURRENT_TIMESTAMP` |


## `projects`

### Columns

| name | type | notnull | pk | default |
|---|---|---:|---:|---|
| `id` | `INTEGER` | 1 | 1 | `` |
| `name` | `VARCHAR(180)` | 1 | 0 | `` |
| `description` | `TEXT` | 0 | 0 | `` |
| `status` | `VARCHAR(9)` | 1 | 0 | `ONGOING` |


## `skills`

### Columns

| name | type | notnull | pk | default |
|---|---|---:|---:|---|
| `id` | `INTEGER` | 1 | 1 | `` |
| `name` | `VARCHAR(120)` | 1 | 0 | `` |
| `normalized_name` | `VARCHAR(120)` | 1 | 0 | `` |


## `tickets`

### Columns

| name | type | notnull | pk | default |
|---|---|---:|---:|---|
| `id` | `INTEGER` | 1 | 1 | `` |
| `employee_id` | `INTEGER` | 1 | 0 | `` |
| `assignee_id` | `INTEGER` | 0 | 0 | `` |
| `title` | `VARCHAR(180)` | 1 | 0 | `` |
| `description` | `TEXT` | 1 | 0 | `` |
| `category` | `VARCHAR(10)` | 1 | 0 | `` |
| `priority` | `VARCHAR(6)` | 1 | 0 | `` |
| `status` | `VARCHAR(11)` | 1 | 0 | `` |
| `created_at` | `DATETIME` | 1 | 0 | `CURRENT_TIMESTAMP` |

