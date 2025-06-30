"""
TSH ERP Migration Dashboard
لوحة معلومات الهجرة

Comprehensive migration control and monitoring dashboard for TSH ERP system.
This dashboard provides a centralized interface for managing data migration from Zoho.
"""

import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class MigrationDashboard:
    """لوحة معلومات الهجرة"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000/api"):
        self.api_base_url = api_base_url
        self.migration_api = f"{api_base_url}/migration"
    
    def make_api_request(self, endpoint: str, method: str = "GET", data: dict = None, files: dict = None):
        """تقديم طلب API"""
        try:
            url = f"{self.api_base_url}/{endpoint}"
            headers = {"Content-Type": "application/json"} if not files else {}
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                if files:
                    response = requests.post(url, data=data, files=files)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                st.error(f"Unsupported HTTP method: {method}")
                return None
            
            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 404:
                st.warning(f"Resource not found: {endpoint}")
                return None
            else:
                st.error(f"API Error ({response.status_code}): {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API server. Please ensure the server is running.")
            return None
        except Exception as e:
            st.error(f"❌ API request failed: {str(e)}")
            return None
    
    def render_dashboard(self):
        """عرض لوحة المعلومات"""
        st.set_page_config(
            page_title="TSH ERP Migration Dashboard",
            page_icon="🚀",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("🚀 TSH ERP Migration Dashboard")
        st.markdown("**لوحة معلومات الهجرة من Zoho إلى TSH ERP**")
        
        # Sidebar Navigation
        with st.sidebar:
            st.header("📋 Navigation")
            page = st.selectbox(
                "Select Page",
                [
                    "Migration Overview",
                    "Create Migration Batch",
                    "Batch Management",
                    "Data Migration",
                    "Reports & Analytics",
                    "Configuration",
                    "Troubleshooting"
                ]
            )
        
        # Main Content
        if page == "Migration Overview":
            self.render_overview_page()
        elif page == "Create Migration Batch":
            self.render_create_batch_page()
        elif page == "Batch Management":
            self.render_batch_management_page()
        elif page == "Data Migration":
            self.render_data_migration_page()
        elif page == "Reports & Analytics":
            self.render_reports_page()
        elif page == "Configuration":
            self.render_configuration_page()
        elif page == "Troubleshooting":
            self.render_troubleshooting_page()
    
    def render_overview_page(self):
        """صفحة النظرة العامة"""
        st.header("📊 Migration Overview")
        
        # Get migration summary
        summary = self.make_api_request("reports/summary")
        
        if summary:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Batches",
                    summary.get('summary', {}).get('total_batches', 0)
                )
            
            with col2:
                st.metric(
                    "Total Records",
                    summary.get('summary', {}).get('total_records', 0)
                )
            
            with col3:
                st.metric(
                    "Success Rate",
                    summary.get('summary', {}).get('success_rate', '0%')
                )
            
            with col4:
                st.metric(
                    "Failed Records",
                    summary.get('summary', {}).get('failed_records', 0)
                )
            
            # Migration Progress Chart
            if summary.get('batches'):
                self.render_migration_progress_chart(summary['batches'])
            
            # Recent Activity
            st.subheader("Recent Migration Activity")
            self.render_recent_activity(summary.get('batches', []))
        
        else:
            st.info("No migration data available yet. Create your first migration batch to get started.")
    
    def render_create_batch_page(self):
        """صفحة إنشاء دفعة الهجرة"""
        st.header("🆕 Create Migration Batch")
        
        with st.form("create_batch_form"):
            st.subheader("Batch Configuration")
            
            batch_name = st.text_input(
                "Batch Name *",
                placeholder="e.g., Zoho Items Migration - December 2024"
            )
            
            description = st.text_area(
                "Description",
                placeholder="Describe the purpose and scope of this migration batch..."
            )
            
            source_system = st.selectbox(
                "Source System *",
                ["ZOHO_BOOKS", "ZOHO_INVENTORY", "ZOHO_BOTH"]
            )
            
            # Migration Configuration
            st.subheader("Migration Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                currency_conversion = st.checkbox(
                    "Enable USD to IQD Conversion",
                    value=True,
                    help="Convert USD prices to IQD using rate 1:1500"
                )
                
                salesperson_mapping = st.checkbox(
                    "Enable Salesperson Mapping",
                    value=True,
                    help="Map customers to salespeople based on deposit accounts"
                )
            
            with col2:
                stock_migration = st.checkbox(
                    "Include Stock Migration",
                    value=True,
                    help="Migrate available stock as stock on hand"
                )
                
                price_list_migration = st.checkbox(
                    "Include Price Lists",
                    value=True,
                    help="Migrate active price lists"
                )
            
            submitted = st.form_submit_button("Create Migration Batch")
            
            if submitted and batch_name:
                config = {
                    "currency_conversion": currency_conversion,
                    "salesperson_mapping": salesperson_mapping,
                    "stock_migration": stock_migration,
                    "price_list_migration": price_list_migration
                }
                
                batch_data = {
                    "batch_name": batch_name,
                    "description": description,
                    "source_system": source_system,
                    "migration_config": config
                }
                
                result = self.make_api_request("batches", "POST", batch_data)
                
                if result:
                    st.success(f"✅ Migration batch created successfully!")
                    st.json(result)
                    st.rerun()
    
    def render_batch_management_page(self):
        """صفحة إدارة الدفعات"""
        st.header("📦 Batch Management")
        
        # Get all batches
        batches = self.make_api_request("batches")
        
        if batches:
            # Batch Status Filter
            col1, col2 = st.columns([3, 1])
            
            with col1:
                status_filter = st.selectbox(
                    "Filter by Status",
                    ["All", "PENDING", "IN_PROGRESS", "COMPLETED", "FAILED", "REQUIRES_REVIEW"]
                )
            
            with col2:
                st.metric("Total Batches", len(batches))
            
            # Batch List
            for batch in batches:
                if status_filter == "All" or batch.get('status') == status_filter:
                    self.render_batch_card(batch)
        
        else:
            st.info("No migration batches found. Create your first batch to get started.")
    
    def render_batch_card(self, batch: Dict[str, Any]):
        """عرض بطاقة الدفعة"""
        with st.expander(f"📦 {batch.get('batch_name', 'Unknown Batch')} - {batch.get('status', 'Unknown')}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Batch Number:** {batch.get('batch_number', 'N/A')}")
                st.write(f"**Source System:** {batch.get('source_system', 'N/A')}")
                st.write(f"**Status:** {batch.get('status', 'N/A')}")
            
            with col2:
                st.write(f"**Total Records:** {batch.get('total_records', 0)}")
                st.write(f"**Successful:** {batch.get('successful_records', 0)}")
                st.write(f"**Failed:** {batch.get('failed_records', 0)}")
            
            with col3:
                st.write(f"**Created:** {batch.get('created_at', 'N/A')}")
                st.write(f"**Started:** {batch.get('start_time', 'N/A')}")
                st.write(f"**Completed:** {batch.get('end_time', 'N/A')}")
            
            if batch.get('description'):
                st.write(f"**Description:** {batch.get('description')}")
            
            # Action Buttons
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if batch.get('status') == 'PENDING':
                    if st.button(f"▶️ Start", key=f"start_{batch.get('id')}"):
                        result = self.make_api_request(f"batches/{batch.get('id')}/start", "PUT")
                        if result:
                            st.success("Batch started!")
                            st.rerun()
            
            with col2:
                if batch.get('status') == 'IN_PROGRESS':
                    if st.button(f"✅ Complete", key=f"complete_{batch.get('id')}"):
                        result = self.make_api_request(f"batches/{batch.get('id')}/complete", "PUT")
                        if result:
                            st.success("Batch completed!")
                            st.rerun()
            
            with col3:
                if batch.get('failed_records', 0) > 0:
                    if st.button(f"🔍 View Errors", key=f"errors_{batch.get('id')}"):
                        self.show_failed_records(batch.get('id'))
            
            with col4:
                if st.button(f"📊 Details", key=f"details_{batch.get('id')}"):
                    self.show_batch_details(batch.get('id'))
    
    def render_data_migration_page(self):
        """صفحة هجرة البيانات"""
        st.header("🔄 Data Migration")
        
        # Select Migration Batch
        batches = self.make_api_request("batches")
        if not batches:
            st.warning("Please create a migration batch first.")
            return
        
        batch_options = {f"{b.get('batch_name')} ({b.get('batch_number')})": b.get('id') for b in batches}
        selected_batch_name = st.selectbox("Select Migration Batch", list(batch_options.keys()))
        selected_batch_id = batch_options[selected_batch_name]
        
        # Migration Method Selection
        st.subheader("Migration Method")
        migration_method = st.radio(
            "Choose migration method:",
            ["Direct from Zoho API", "Upload Files", "Manual Data Entry"]
        )
        
        if migration_method == "Direct from Zoho API":
            self.render_zoho_api_migration(selected_batch_id)
        elif migration_method == "Upload Files":
            self.render_file_upload_migration(selected_batch_id)
        else:
            self.render_manual_migration(selected_batch_id)
    
    def render_zoho_api_migration(self, batch_id: int):
        """هجرة من Zoho API مباشرة"""
        st.subheader("🌐 Direct Zoho API Migration")
        
        # Zoho Configuration
        with st.expander("⚙️ Zoho API Configuration", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                organization_id = st.text_input("Organization ID", key="zoho_org_id")
                access_token = st.text_input("Access Token", type="password", key="zoho_access_token")
                client_id = st.text_input("Client ID", key="zoho_client_id")
            
            with col2:
                refresh_token = st.text_input("Refresh Token", type="password", key="zoho_refresh_token")
                client_secret = st.text_input("Client Secret", type="password", key="zoho_client_secret")
        
        if not all([organization_id, access_token]):
            st.warning("Please provide at least Organization ID and Access Token")
            return
        
        # Test Connection Button
        if st.button("🔗 Test Zoho Connection", key="test_zoho_connection"):
            zoho_config = {
                "organization_id": organization_id,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "client_id": client_id,
                "client_secret": client_secret
            }
            
            # Test connection by extracting a small sample
            try:
                result = self.make_api_request("extract-zoho-data", "POST", {
                    "data_type": "items",
                    "zoho_config": zoho_config
                })
                
                if result:
                    st.success("✅ Connection successful!")
                    st.write(f"Found {result.get('total_records', 0)} items")
                    
                    # Show preview
                    if result.get('data'):
                        st.subheader("📋 Data Preview")
                        st.json(result['data'][:3])  # Show first 3 records
                else:
                    st.error("❌ Connection failed")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")
        
        # Data Type Selection and Migration
        st.subheader("� Select Data to Migrate")
        
        data_types = ["items", "customers", "vendors", "price_lists"]
        
        for data_type in data_types:
            with st.expander(f"�📦 {data_type.title()}", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"👁️ Preview {data_type.title()}", key=f"preview_{data_type}"):
                        if organization_id and access_token:
                            zoho_config = {
                                "organization_id": organization_id,
                                "access_token": access_token,
                                "refresh_token": refresh_token,
                                "client_id": client_id,
                                "client_secret": client_secret
                            }
                            
                            result = self.make_api_request("extract-zoho-data", "POST", {
                                "data_type": data_type,
                                "zoho_config": zoho_config
                            })
                            
                            if result:
                                st.success(f"Found {result.get('total_records', 0)} {data_type}")
                                if result.get('data'):
                                    st.dataframe(pd.DataFrame(result['data']))
                
                with col2:
                    if st.button(f"🚀 Migrate {data_type.title()}", key=f"migrate_{data_type}"):
                        if organization_id and access_token:
                            zoho_config = {
                                "organization_id": organization_id,
                                "access_token": access_token,
                                "refresh_token": refresh_token,
                                "client_id": client_id,
                                "client_secret": client_secret
                            }
                            
                            with st.spinner(f"Migrating {data_type}..."):
                                result = self.make_api_request(
                                    f"batches/{batch_id}/migrate-from-zoho-api", 
                                    "POST", 
                                    {
                                        "data_type": data_type,
                                        "zoho_config": zoho_config
                                    }
                                )
                                
                                if result:
                                    st.success(f"✅ {data_type.title()} migration completed!")
                                    
                                    results = result.get('results', {})
                                    col_a, col_b, col_c = st.columns(3)
                                    
                                    with col_a:
                                        st.metric("Total", results.get('total_records', 0))
                                    with col_b:
                                        st.metric("Success", results.get('successful_records', 0))
                                    with col_c:
                                        st.metric("Failed", results.get('failed_records', 0))
                
                with col3:
                    if st.button(f"📊 View Results", key=f"results_{data_type}"):
                        # Show migration results for this data type
                        self.show_migration_results(batch_id, data_type)
    
    def render_file_upload_migration(self, batch_id: int):
        """هجرة من الملفات المرفوعة"""
        st.subheader("📂 File Upload Migration")
        
        data_types = ["items", "customers", "vendors", "stock", "price_lists"]
        
        for data_type in data_types:
            with st.expander(f"📁 Upload {data_type.title()} File", expanded=False):
                uploaded_file = st.file_uploader(
                    f"Choose {data_type} file", 
                    type=['csv', 'xlsx', 'xls'],
                    key=f"upload_{data_type}"
                )
                
                if uploaded_file is not None:
                    # Show file preview
                    try:
                        if uploaded_file.name.endswith('.csv'):
                            df = pd.read_csv(uploaded_file)
                        else:
                            df = pd.read_excel(uploaded_file)
                        
                        st.write(f"**File:** {uploaded_file.name}")
                        st.write(f"**Records:** {len(df)}")
                        st.dataframe(df.head())
                        
                        if st.button(f"🚀 Migrate {data_type.title()}", key=f"migrate_file_{data_type}"):
                            # Reset file pointer
                            uploaded_file.seek(0)
                            
                            # Create form data
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                            data = {"file_type": data_type}
                            
                            with st.spinner(f"Migrating {data_type} from file..."):
                                result = self.make_api_request(
                                    f"batches/{batch_id}/migrate-from-file",
                                    "POST",
                                    data,
                                    files=files
                                )
                                
                                if result:
                                    st.success(f"✅ {data_type.title()} migration completed!")
                                    
                                    results = result.get('results', {})
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        st.metric("Total", results.get('total_records', 0))
                                    with col2:
                                        st.metric("Success", results.get('successful_records', 0))
                                    with col3:
                                        st.metric("Failed", results.get('failed_records', 0))
                    
                    except Exception as e:
                        st.error(f"Error reading file: {str(e)}")
    
    def render_manual_migration(self, batch_id: int):
        """هجرة يدوية"""
        st.subheader("✍️ Manual Data Entry Migration")
        
        # Migration Steps
        tabs = st.tabs([
            "📦 Items & Categories",
            "💰 Price Lists", 
            "👥 Customers",
            "🏭 Vendors",
            "📊 Stock Levels"
        ])
        
        with tabs[0]:
            self.render_items_migration_tab(batch_id)
        
        with tabs[1]:
            self.render_price_lists_migration_tab(batch_id)
        
        with tabs[2]:
            self.render_customers_migration_tab(batch_id)
        
        with tabs[3]:
            self.render_vendors_migration_tab(batch_id)
        
        with tabs[4]:
            self.render_stock_migration_tab(batch_id)
    
    def render_items_migration_tab(self, batch_id: int):
        """تبويب هجرة الأصناف"""
        st.markdown("### 📦 Items & Categories Migration")
        st.markdown("**Convert USD prices to IQD (1:1500 rate)**")
        
        # Sample data input
        st.subheader("Sample Items Data")
        
        sample_items = [
            {
                "item_id": "ITEM001",
                "name": "Laptop Dell Inspiron 15",
                "sku": "DELL-INS-15-001",
                "category_name": "Electronics",
                "selling_price": 800.00,  # USD
                "cost_price": 600.00,  # USD
                "stock_on_hand": 25,
                "reorder_level": 5,
                "status": "active"
            },
            {
                "item_id": "ITEM002", 
                "name": "iPhone 15 Pro",
                "sku": "APPL-IP15-PRO",
                "category_name": "Mobile",
                "selling_price": 1200.00,  # USD
                "cost_price": 900.00,  # USD
                "stock_on_hand": 15,
                "reorder_level": 3,
                "status": "active"
            }
        ]
        
        df_items = pd.DataFrame(sample_items)
        
        # Show conversion preview  
        df_items['selling_price_iqd'] = df_items['selling_price'] * 1500
        df_items['cost_price_iqd'] = df_items['cost_price'] * 1500
        
        st.dataframe(df_items)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Migrate Items", key="migrate_items"):
                result = self.make_api_request(f"batches/{batch_id}/migrate-items", "POST", sample_items)
                if result:
                    st.success("✅ Items migration completed!")
                    st.json(result)
        
        with col2:
            if st.button("📂 Upload Items File", key="upload_items"):
                st.info("File upload functionality will be implemented here")
    
    def render_customers_migration_tab(self, batch_id: int):
        """تبويب هجرة العملاء"""
        st.markdown("### 👥 Customers Migration")
        st.markdown("**Automatic salesperson assignment based on deposit accounts**")
        
        # Salesperson Mapping Info
        with st.expander("🗺️ Salesperson Mapping Rules"):
            mapping_config = self.make_api_request("config/salesperson-mapping")
            if mapping_config:
                st.json(mapping_config)
        
        # Sample customers data
        sample_customers = [
            {
                "customer_id": "CUST001",
                "customer_name": "Baghdad Electronics Store",
                "email": "info@baghdadelectronics.com",
                "phone": "+964770123456",
                "currency": "IQD",
                "outstanding_receivable": 2500000.0,  # IQD
                "deposit_account": "frati_deposit_account",  # Maps to Ayad
                "price_list_name": "Retail Price List",
                "status": "active"
            },
            {
                "customer_id": "CUST002",
                "customer_name": "Basra Tech Solutions",
                "email": "contact@basratech.com",
                "phone": "+964771234567",
                "currency": "IQD",
                "outstanding_receivable": 1800000.0,  # IQD
                "deposit_account": "southi_deposit_account",  # Maps to Haider
                "price_list_name": "Wholesale Price List",
                "status": "active"
            }
        ]
        
        df_customers = pd.DataFrame(sample_customers)
        st.dataframe(df_customers)
        
        if st.button("🚀 Migrate Customers", key="migrate_customers"):
            result = self.make_api_request(f"batches/{batch_id}/migrate-customers", "POST", sample_customers)
            if result:
                st.success("✅ Customers migration completed!")
                st.json(result)
    
    def render_reports_page(self):
        """صفحة التقارير والتحليلات"""
        st.header("📊 Reports & Analytics")
        
        # Migration Summary
        summary = self.make_api_request("reports/summary")
        
        if summary:
            # Success Rate Chart
            col1, col2 = st.columns(2)
            
            with col1:
                self.render_success_rate_chart(summary)
            
            with col2:
                self.render_entity_breakdown_chart(summary)
            
            # Salesperson Customer Mapping
            st.subheader("👥 Salesperson Customer Mapping")
            mapping = self.make_api_request("reports/salesperson-mapping")
            
            if mapping:
                self.render_salesperson_mapping_report(mapping)
        
        else:
            st.info("No migration data available for reporting.")
    
    def render_configuration_page(self):
        """صفحة الإعدادات"""
        st.header("⚙️ Configuration")
        
        # Exchange Rates
        st.subheader("💱 Exchange Rates")
        rates = self.make_api_request("config/exchange-rates")
        
        if rates:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("USD to IQD", "1:1500")
                st.metric("USD to RMB", "1:7.2")
            
            with col2:
                st.json(rates.get('exchange_rates', {}))
        
        # Test Currency Conversion
        st.subheader("🧪 Test Currency Conversion")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            test_amount = st.number_input("Amount", value=100.0, min_value=0.0)
        
        with col2:
            from_currency = st.selectbox("From", ["USD", "IQD", "RMB"])
        
        with col3:
            to_currency = st.selectbox("To", ["IQD", "USD", "RMB"])
        
        if st.button("🔄 Convert"):
            result = self.make_api_request(
                f"utils/test-currency-conversion?amount={test_amount}&from_currency={from_currency}&to_currency={to_currency}",
                "POST"
            )
            if result:
                st.success(f"✅ {test_amount} {from_currency} = {result.get('converted', {}).get('amount', 0)} {to_currency}")
    
    def render_troubleshooting_page(self):
        """صفحة استكشاف الأخطاء"""
        st.header("🔧 Troubleshooting")
        
        # System Health Check
        st.subheader("🏥 System Health Check")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 Check API Connection"):
                try:
                    response = requests.get(f"{self.api_base_url}/")
                    if response.status_code == 200:
                        st.success("✅ API connection is healthy")
                    else:
                        st.error(f"❌ API connection failed: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
        
        with col2:
            if st.button("🔍 Check Database Connection"):
                # This would need to be implemented in the API
                st.info("Database health check not implemented yet")
        
        # Failed Records Analysis
        st.subheader("❌ Failed Records Analysis")
        
        batches = self.make_api_request("batches")
        if batches:
            failed_batches = [b for b in batches if b.get('failed_records', 0) > 0]
            
            if failed_batches:
                selected_batch = st.selectbox(
                    "Select Batch with Failures",
                    [f"{b.get('batch_name')} ({b.get('failed_records')} failures)" for b in failed_batches]
                )
                
                batch_id = failed_batches[0].get('id')  # Simplified selection
                
                failed_records = self.make_api_request(f"reports/failed-records/{batch_id}")
                
                if failed_records:
                    st.dataframe(pd.DataFrame(failed_records))
            else:
                st.success("✅ No failed records found!")
    
    # Helper Methods for Charts and Visualizations
    
    def render_migration_progress_chart(self, batches: List[Dict]):
        """مخطط تقدم الهجرة"""
        if not batches:
            return
        
        df = pd.DataFrame(batches)
        
        fig = px.bar(
            df,
            x='batch_name',
            y=['successful_records', 'failed_records'],
            title='Migration Progress by Batch',
            barmode='stack'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_success_rate_chart(self, summary: Dict):
        """مخطط معدل النجاح"""
        summary_data = summary.get('summary', {})
        
        successful = summary_data.get('successful_records', 0)
        failed = summary_data.get('failed_records', 0)
        
        fig = go.Figure(data=[go.Pie(
            labels=['Successful', 'Failed'],
            values=[successful, failed],
            hole=0.3
        )])
        
        fig.update_layout(title_text="Migration Success Rate")
        st.plotly_chart(fig, use_container_width=True)
    
    def render_entity_breakdown_chart(self, summary: Dict):
        """مخطط تفصيل الكيانات"""
        # This would need entity-specific data from the API
        st.info("Entity breakdown chart - data structure needs to be implemented")
    
    def render_salesperson_mapping_report(self, mapping: Dict):
        """تقرير ربط مندوبي المبيعات"""
        mapped_customers = mapping.get('mapped_customers', {})
        
        if mapped_customers:
            for salesperson, customers in mapped_customers.items():
                with st.expander(f"👤 {salesperson} - {len(customers)} customers"):
                    df = pd.DataFrame(customers)
                    st.dataframe(df)
                    
                    total_outstanding = sum(c.get('outstanding_receivable', 0) for c in customers)
                    st.metric("Total Outstanding Receivables", f"{total_outstanding:,.0f}")
        
        unmapped = mapping.get('unmapped_customers', [])
        if unmapped:
            st.warning(f"⚠️ {len(unmapped)} customers could not be mapped to salespeople")
            with st.expander("View Unmapped Customers"):
                st.dataframe(pd.DataFrame(unmapped))
    
    def show_failed_records(self, batch_id: int):
        """عرض السجلات الفاشلة"""
        failed_records = self.make_api_request(f"reports/failed-records/{batch_id}")
        
        if failed_records:
            st.subheader(f"❌ Failed Records for Batch {batch_id}")
            df = pd.DataFrame(failed_records)
            st.dataframe(df)
        else:
            st.success("✅ No failed records found!")
    
    def show_batch_details(self, batch_id: int):
        """عرض تفاصيل الدفعة"""
        batch = self.make_api_request(f"batches/{batch_id}")
        
        if batch:
            st.subheader(f"📦 Batch Details: {batch.get('batch_name')}")
            st.json(batch)
    
    def show_migration_results(self, batch_id: int, data_type: str):
        """عرض نتائج الهجرة"""
        st.subheader(f"📊 Migration Results - {data_type.title()}")
        
        # Get migration records for this batch and data type
        records = self.make_api_request(f"batches/{batch_id}/records")
        
        if records:
            # Filter by data type
            filtered_records = [r for r in records if r.get('entity_type', '').lower() == data_type.upper()]
            
            if filtered_records:
                df = pd.DataFrame(filtered_records)
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                total = len(filtered_records)
                success = len([r for r in filtered_records if r.get('status') == 'COMPLETED'])
                failed = len([r for r in filtered_records if r.get('status') == 'FAILED'])
                pending = len([r for r in filtered_records if r.get('status') == 'PENDING'])
                
                with col1:
                    st.metric("Total Records", total)
                with col2:
                    st.metric("Successful", success)
                with col3:
                    st.metric("Failed", failed)
                with col4:
                    st.metric("Pending", pending)
                
                # Show records table
                st.dataframe(df[['source_id', 'target_id', 'status', 'error_message', 'processed_at']])
                
                # Show failed records details
                if failed > 0:
                    st.subheader("❌ Failed Records")
                    failed_records = [r for r in filtered_records if r.get('status') == 'FAILED']
                    for record in failed_records:
                        with st.expander(f"Record: {record.get('source_id')}"):
                            st.write(f"**Error:** {record.get('error_message')}")
                            st.json(record.get('source_data', {}))
            else:
                st.info(f"No {data_type} records found for this batch.")
        else:
            st.error("Failed to load migration records.")
    


# Main Application Entry Point
def main():
    """نقطة دخول التطبيق الرئيسية"""
    dashboard = MigrationDashboard()
    dashboard.render_dashboard()


if __name__ == "__main__":
    main()
