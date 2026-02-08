# Research Checklist

Execute these searches before PRD development. Do not rely on training data.

## Required Searches

```
□ "Replit Agent [current year] capabilities features"
□ "Replit database storage [current year]" 
□ "Replit App Storage object storage"
□ "Replit Agent best practices prompting"
□ "[specific technology] Replit [current year]" (per major tech)
□ "Replit deployment autoscale [current year]"
```

## Native Services to Verify

### Replit Database (PostgreSQL)
- Implementation (Neon-hosted? Native?)
- Environment variables (DATABASE_URL)
- ORM recommendations (Drizzle, Prisma)

### Replit App Storage
- SDK availability (JavaScript, Python)
- Bucket configuration
- File size limits

### Replit Auth
- Current status and integration pattern

### Deployment
- Autoscale vs Reserved VM
- Domain configuration

## Framework Assessment

```
□ Which frameworks have "curated app type" status?
□ Current stable versions
□ Known incompatibilities
```

## Output

Before writing prompts, document:

| Category | Finding |
|----------|---------|
| Native services | (prefer Replit-native) |
| Framework | (based on Agent support) |
| Package versions | (as of search date) |
| Constraints | (platform limitations) |
