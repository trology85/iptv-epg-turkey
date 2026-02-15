name: Update EPG Daily

on:
  schedule:
    # Her gün saat 03:00 UTC'de çalış (Türkiye saati 06:00)
    - cron: '0 3 * * *'
  
  # Manuel tetikleme
  workflow_dispatch:

jobs:
  update-epg:
    runs-on: ubuntu-latest
    
    steps:
      - name: 📥 Checkout repository
        uses: actions/checkout@v4
      
      - name: 🐍 Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: 📦 Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests
      
      - name: 🔄 Update EPG
        run: python scripts/update_epg_v2.py
      
      - name: 📊 Check changes
        id: check_changes
        run: |
          if git diff --quiet; then
            echo "changed=false" >> $GITHUB_OUTPUT
            echo "ℹ️  Değişiklik yok, commit atlanıyor"
          else
            echo "changed=true" >> $GITHUB_OUTPUT
            echo "✅ Değişiklik tespit edildi"
          fi
      
      - name: 💾 Commit and push
        if: steps.check_changes.outputs.changed == 'true'
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add epg/epg_turkey.xml
          git commit -m "🔄 EPG güncellendi - $(date +'%Y-%m-%d %H:%M:%S UTC')"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: 🎉 Success
        if: steps.check_changes.outputs.changed == 'true'
        run: echo "✅ EPG başarıyla güncellendi ve push edildi!"
