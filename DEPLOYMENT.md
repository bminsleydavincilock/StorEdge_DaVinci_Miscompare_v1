# 🚀 Deployment Guide - StorEdge DaVinci Analyzer

This guide will help you deploy the StorEdge DaVinci Unit Status Analyzer to Streamlit Cloud.

## 📋 Prerequisites

- GitHub account
- Streamlit Cloud account (free)
- Supabase account (free tier available)

## 🔧 Setup Steps

### 1. Prepare Your Repository

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Add Streamlit web application"
   git push origin main
   ```

2. **Ensure your repository structure includes:**
   ```
   StorEdge_DaVinci_Miscompare_v1/
   ├── streamlit_app.py          # Main Streamlit app
   ├── requirements.txt          # Python dependencies
   ├── .streamlit/
   │   ├── config.toml          # Streamlit configuration
   │   └── secrets.toml         # Secrets template
   ├── src/
   │   ├── unit_status_analyzer.py
   │   ├── report_generator.py
   │   ├── enhanced_excel_exporter.py
   │   └── supabase_integration.py
   └── web_config.py
   ```

### 2. Set Up Supabase Database

1. **Log into your Supabase dashboard**
2. **Create the required tables** by running this SQL in the SQL Editor:

   ```sql
   -- Analysis Sessions Table
   CREATE TABLE IF NOT EXISTS analysis_sessions (
       id SERIAL PRIMARY KEY,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       user_email TEXT,
       total_units INTEGER,
       miscompare_count INTEGER,
       high_severity_count INTEGER,
       analysis_summary JSONB,
       file_names JSONB,
       status TEXT DEFAULT 'completed'
   );
   
   -- Analysis Results Table
   CREATE TABLE IF NOT EXISTS analysis_results (
       id SERIAL PRIMARY KEY,
       session_id INTEGER REFERENCES analysis_sessions(id),
       unit TEXT,
       unit_status TEXT,
       final_status TEXT,
       actual_lock_status TEXT,
       expected_lock_status TEXT,
       is_miscompare BOOLEAN,
       miscompare_severity TEXT,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );
   
   -- Create indexes for better performance
   CREATE INDEX IF NOT EXISTS idx_analysis_sessions_user_email ON analysis_sessions(user_email);
   CREATE INDEX IF NOT EXISTS idx_analysis_sessions_created_at ON analysis_sessions(created_at);
   CREATE INDEX IF NOT EXISTS idx_analysis_results_session_id ON analysis_results(session_id);
   CREATE INDEX IF NOT EXISTS idx_analysis_results_unit ON analysis_results(unit);
   ```

3. **Get your Supabase credentials:**
   - Project URL
   - Anon key
   - Database password

### 3. Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in with your GitHub account**
3. **Click "New app"**
4. **Fill in the deployment form:**
   - **Repository:** `your-username/StorEdge_DaVinci_Miscompare_v1`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
   - **App URL:** `storedge-davinci-analyzer` (or your preferred name)

5. **Configure secrets** in the Streamlit Cloud dashboard:
   - Go to your app's settings
   - Click "Secrets"
   - Add the following secrets:

   ```toml
   [supabase]
   url = "https://your-project.supabase.co"
   anon_key = "your-anon-key"
   email = "your-email"
   password = "your-password"
   
   [database]
   host = "db.your-project.supabase.co"
   port = "5432"
   database = "postgres"
   username = "postgres"
   password = "your-db-password"
   schema = "public"
   
   [app]
   title = "StorEdge DaVinci Unit Status Analyzer"
   description = "Analyze self-storage unit status and lock assignments"
   version = "1.0.0"
   max_file_size = 52428800
   ```

6. **Deploy the app**
   - Click "Deploy!"
   - Wait for the deployment to complete (usually 2-5 minutes)

### 4. Test Your Deployment

1. **Visit your deployed app URL**
2. **Upload sample CSV files**
3. **Run an analysis**
4. **Verify all features work correctly**

## 🔒 Security Considerations

### Environment Variables
- Never commit sensitive credentials to your repository
- Use Streamlit Cloud's secrets management
- Rotate credentials regularly

### File Upload Security
- The app validates file types and sizes
- Files are processed in temporary directories
- No permanent storage of uploaded files

### Database Security
- Use Supabase's built-in security features
- Enable Row Level Security (RLS) if needed
- Monitor database usage and costs

## 📊 Monitoring and Maintenance

### Streamlit Cloud
- Monitor app usage in the Streamlit Cloud dashboard
- Check logs for errors
- Update dependencies regularly

### Supabase
- Monitor database usage and costs
- Set up alerts for unusual activity
- Regular backups (automatic with Supabase)

### Performance Optimization
- Monitor app performance
- Optimize database queries
- Consider caching for frequently accessed data

## 🚨 Troubleshooting

### Common Issues

1. **App won't start:**
   - Check `requirements.txt` for all dependencies
   - Verify `streamlit_app.py` is in the root directory
   - Check Streamlit Cloud logs

2. **Database connection errors:**
   - Verify Supabase credentials in secrets
   - Check if tables exist in Supabase
   - Test connection with Supabase dashboard

3. **File upload issues:**
   - Check file size limits
   - Verify CSV format requirements
   - Check browser console for errors

4. **Analysis failures:**
   - Check file column names match requirements
   - Verify data formats
   - Check Streamlit Cloud logs for detailed errors

### Getting Help

- Check Streamlit Cloud documentation
- Review Supabase documentation
- Check GitHub issues in your repository
- Contact support if needed

## 🔄 Updates and Maintenance

### Updating the App
1. Make changes to your code
2. Commit and push to GitHub
3. Streamlit Cloud will automatically redeploy

### Updating Dependencies
1. Update `requirements.txt`
2. Test locally first
3. Commit and push changes
4. Monitor deployment for issues

### Database Maintenance
- Regular cleanup of old analysis sessions
- Monitor storage usage
- Update database schema as needed

## 📈 Scaling Considerations

### For High Usage
- Consider upgrading Supabase plan
- Implement caching strategies
- Add rate limiting
- Consider load balancing

### For Enterprise Use
- Add user authentication
- Implement audit logging
- Add data encryption
- Consider on-premises deployment

## 🎯 Next Steps

After successful deployment:

1. **Share your app** with stakeholders
2. **Gather user feedback**
3. **Monitor usage patterns**
4. **Plan feature enhancements**
5. **Consider additional integrations**

Your StorEdge DaVinci Analyzer is now live and ready to help users analyze their self-storage unit data!
